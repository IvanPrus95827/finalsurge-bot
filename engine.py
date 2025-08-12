from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def generate_answer(subject, body):
    prompt_template = f'''
I'm the coach of the athlete. There is the replying message from the athlete for my message. Are there any needs to reply to it?
For example, in these cases, you don't need reply. 
examples: [
{{'subject':'Hello', 'body':'ok'}},
{{ 'subject':'RE: Nice work on Final Surge this week!', 'body':'Text'}},
{{'subject':'Well done on the training', 'body':'Thanks Eoin. A good start to August😊 also I am happy to sign up for the year if you let me know the details. I’m enjoying it all classes training talks. M'}}
]
Please give me the answer with only yes or no.
If it is yes, please give me the resonable and human-like respond that should sent to athletes with 1-2 sentences format like this.
{{"status": "yes", "answer": "........."}}
If it is no, please give me the answer with only no like this.
{{"status": "no"}}
This is the message from athlete.
{{
    subject: "{subject}"
    body: "{body}"
}}
'''


    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt_template
    )
    result = response.text.replace("```json", "").replace("```", "")
    json_response = json.loads(result)
    return json_response

if __name__ == "__main__":
    # test cases
    print(generate_answer(
        "Well done on training!",
        '''
Hi Eoin, yes I might give this Norwegian thing a go, 3 Threshold sessions a week typically.... I have the National Half Marathon in Tullamore at end of August, a bit too close for comfort but I'll give it a go anyway, hoping all the Threshold will help. Lucan 5m after that. I'll let you know if I want to change back away from the Norwegian Singles Method.
        '''
    ))