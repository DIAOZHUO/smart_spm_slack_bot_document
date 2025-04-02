## Leveraging Large Language Model and Social Network Service for Automation in Scanning Probe Microscopy

### Installation

The code runs the code in python 3.11. 


```bash
pip install -r requirements.txt
```

### Setup

This project uses the functions in [slack api](https://api.slack.com/)
and [OpenAI api](https://platform.openai.com/docs/overview).
Please obtain the API TOKEN from the corresponding website and enter it into `api_key.py`.


```python
SLACK_APP_TOKEN = ""
SLACK_BOT_TOKEN = ""
open_ai_key = ""
```


Additionally, this project has removed scripts related to the SPM device, retaining only the backend processing for Slack.
However, [text2command_parser.py](Util/SlackBot/text2command_parser.py) still includes SPM-related data processing for reference.
When using this project, please comment out any irrelevant code in `text2command_parser.py`.



### Citation

We will be appreciated if you can cite our work!

Zhuo Diao, Hayato Yamashita, Masayuki Abe, Meas.Sci.Technol., 36, 047001 (2025); 
https://doi.org/10.1088/1361-6501/adbf3a