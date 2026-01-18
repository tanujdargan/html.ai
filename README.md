# backend summary (super concise)

Core backend logic:
- /tagAi → return variant A or B
- /rewardTag → update scores + trigger re-render if losing
- Re-render calls OpenAI to generate small improvements

Main files:
- aiBackend/server.py
- sdk/src/AiOptimizeElement_v2.js  ← frontend custom tag logic


# example MongoDB structure (real output)

{
  _id: ObjectId("696cf416f830279cefe924c6"),
  user_id: "guest",
  components: {
    hero: {
      A: {
        current_html: "<div class='section hero'>...</div>",
        current_score: 3,
        number_of_trials: 10,
        history: []
      },
      B: {
        current_html: "<div class='section hero'>... improved ...</div>",
        current_score: 3,
        number_of_trials: 10,
        history: []
      }
    },
    footer: {
      A: {
        current_html: "<div class='section footer'>...</div>",
        current_score: 3,
        number_of_trials: 10,
        history: []
      },
      B: {
        current_html: "<div class='section footer'>... improved ...</div>",
        current_score: 3,
        number_of_trials: 10,
        history: []
      }
    }

  }
}
