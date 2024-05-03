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
uvicorn api.main:app --reload --port=8080 --timeout-keep-alive 120
```

Check `http://127.0.0.1:8080/docs` for OPENAPI documentation.


### Contribute

#### Run presubmit before commit
```
./tools/presubmit.sh
```

#### Create a Pull Request
Always create a branch based off of `main`.
When merging the PR, select `Squash and merge`.

#### Deploy to production
```
git checkout production
git pull --rebase
git merge origin/main
git push
```
