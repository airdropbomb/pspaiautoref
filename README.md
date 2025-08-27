# pspaiautoref

## Instalation

1. **Clone The Repositories:**
   ```bash
   git clone https://github.com/airdropbomb/pspaiautoref.git && cd pspaiautoref
   ```

2. **Install Requirements:**
   ```bash
   pip install -r requirements.txt #or pip3 install -r requirements.txt
   ```

## Configuration

- **ref_code.txt:** You need to input your refer code
  ```bash
    yourrefcode
  ```
- **proxy.txt:** You will find the file `proxy.txt` inside the project directory. Make sure `proxy.txt` contains data that matches the format expected by the script. Here are examples of file formats:
  ```bash
    ip:port # Default Protcol HTTP.
    protocol://ip:port
    protocol://user:pass@ip:port
  ```

  ## Run

```bash
python bot.py #or python3 bot.py
```
