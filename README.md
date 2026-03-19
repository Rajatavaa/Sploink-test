# AI Agent System

## Install
```bash
pip install -r requirements.txt
```

## Setup
Create `.env` file:
```
GROQ_API_KEY=your_api_key_here
```

## Usage Modes

### Mode 1: CLI (Single User)
```bash
cd src
python main.py
```
Enter commands:
- `summarize <text>` - Summarize text
- `what is <topic>` - Research topic
- `calculate 2+2` - Math
- `write <prompt>` - Generate content
- `exit` - Quit

**Note**: Multiple requests within CLI are processed **concurrently**.

---

### Mode 2: Web Server (Multi-User)


#### Start Server
```bash
cd src
python main.py
```
Server runs at `http://localhost:5137`


#### Client Script (Multiple Terminals)

**Terminal 1**: Start server
```bash
python main.py
```

**Terminal 2+**: Run client
```bash
python client.py
```

Client commands:
- `submit <text>` - Submit request
- `check <id>` - Check status
- `poll <id>` - Poll until complete
- `list` - List all requests
- `health` - Server health
- `clear` - Clear completed

**Interactive Mode**
```bash
python client.py -i
```

---

## Architecture

### CLI Mode
- Single process, single user
- Async concurrent processing
- Sequential input, concurrent execution

### Web Server Mode
- **Server**: Handles multiple concurrent requests
- **Request Queue**: In-memory queue with unique IDs
- **Async Processing**: All agent calls are non-blocking
- **Scalability**: Multiple clients can connect simultaneously
- **Background Tasks**: Requests processed asynchronously

### Multi-User Support
```bash
# Terminal 1: Server
python main.py

# Terminal 2: User A
python client.py

# Terminal 3: User B
python client.py

# Terminal 4: User C
python client.py
```

All users share the same server with **concurrent request processing**.

---

## Environment Variables

```
GROQ_API_KEY=your_api_key_here
```
