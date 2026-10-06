# Question A — Level 3 Prediction

**Prediction committed before the experiment:**

If the rolling-window size is doubled from 30 seconds to 60 seconds, I
predict that recall for silent drift will decrease.

Reason: silent drift is a gradual 15 bpm increase over five minutes.
A larger local window should make the gradual change less unusual
relative to the surrounding observations, so fewer points should cross
the z-score threshold.

I expect sharp spikes and drop-outs to be less affected.

Run the experiment only after committing this file.
