"""Historical metadata and cancellable requests on the existing restricted backend."""

import asyncio

from .ibkr import make_backend


class HistoricalTimeout(TimeoutError):
    def __init__(self, bars):
        super().__init__("historical request timeout")
        self.bars = list(bars)


def make_depth_backend():
    # Reuse the pinned low-level handshake, account-sync suppression, qualification
    # and safe diagnostics. No high-level IB.connect/connectAsync is called.
    base = make_backend()
    from ib_async import BarDataList, util

    class Backend:
        client_version = base.client_version
        errors = base.errors
        connect = base.connect
        qualify = base.qualify
        disconnect = base.disconnect

        async def historical(self, contract, params):
            # ib_async 2.1.0's high-level helper cancels on its own timeout, but
            # not on external task cancellation. Keep the same native request
            # protocol and explicitly cancel on either interruption. Partial
            # timeout rows are retained for diagnostics, never counted as success.
            ib = base.ib
            req_id = ib.client.getReqId()
            bars = BarDataList()
            bars.reqId, bars.contract = req_id, contract
            future = ib.wrapper.startReq(req_id, contract, container=bars)
            ib.client.reqHistoricalData(req_id, contract, util.formatIBDatetime(params["endDateTime"]),
                params["durationStr"], params["barSizeSetting"], params["whatToShow"],
                params["useRTH"], params["formatDate"], False, [])
            try:
                await asyncio.wait_for(future, params["timeout"])
            except TimeoutError:
                ib.client.cancelHistoricalData(req_id)
                raise HistoricalTimeout(bars) from None
            except BaseException:
                ib.client.cancelHistoricalData(req_id)
                raise
            return bars

        async def head_timestamp(self, contract):
            ib = base.ib
            req_id = ib.client.getReqId()
            future = ib.wrapper.startReq(req_id, contract)
            ib.client.reqHeadTimeStamp(req_id, contract, "TRADES", True, 2)
            try:
                return await asyncio.wait_for(future, 30)
            finally:
                # Head requests remain active at IB until cancelled, even after
                # a successful response. Always close this historical request.
                ib.client.cancelHeadTimeStamp(req_id)

    return Backend()
