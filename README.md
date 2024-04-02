# Asian Math Pro

### Installation

```bash
git clone git@github.com:Cherolfu/asian_math_pro.git
cd asian_math_pro
pip install -r requirements.txt
```

### Edit your `.env`

```bash
cp .env.example .env
# Edit .env file with your settings
```
### Run the app

```bash
# How to run the application
uvicorn src.main:app --reload --port=8080 --timeout-keep-alive 120
```

Check `http://127.0.0.1:8080/docs` for OPENAI documentation.


### Contribute

#### Formatting before commit
```
pre-commit run --all-files
```
