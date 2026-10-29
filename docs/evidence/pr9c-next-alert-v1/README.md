# Sealed next-alert projection

The prediction.json and rules.json bytes are identical to the local sealed forecast. hashes.json seals this derived projection; local-prediction-hashes.json pins the full native-view prediction bundle, whose hash is reported in the research report. The private input-view.json stays local; its exact hash is retained here. Full semantic replay uses the retained local bundle, while the public prediction and rules remain readable without brokerage or subscriber access. No genuine later alert or forward evaluation is included.
