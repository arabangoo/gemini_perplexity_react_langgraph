## [Gemini Perplexity React LangGraph 풀스택 웹페이지]    
   
본 테스트의 목표는 Gemini-React-LangGraph를 이용한 풀스택 웹페이지를 구축하는 것이다.   
본 테스트에는 Gemini API 키와 Perplexity API 키가 필요하니 미리 발급받아 놓자.   
   
본 테스트의 방향대로 구축이 완료되면 로컬 PC에서 아래와 같은 기능의 서비스를 사용할 수 있다.   
1. Perplexity 최신 검색   
2. Gemini 심층 분석   
3. 세션 기반 대화 기억   
4. 브라우저 닫으면 삭제         
<br/>
   
(1) 윈도우 로컬 PC에서 서비스를 올려보도록 하겠다.   
아래와 같은 명령어로 필수 프로그램의 버전을 먼저 확인해본다.          
   
명령어 (1)  : python --version
명령어 (2) : node --version
명령어 (3) : npm --version
<img width="500" height="160" alt="image_1" src="https://github.com/user-attachments/assets/c2453554-2cc6-42e4-b172-1acfe3b53084" />
<br/>
                   
(2) GitHub 리포지토리에 올라가 있는 파일 구성은 아래와 같다.   
```txt
├── 실행 관련 파일들 
│   ├── install.bat          ← 의존성 설치 자동화
│   ├── run-backend.bat      ← 백엔드만 실행
│   ├── run-frontend.bat     ← 프론트엔드만 실행
│   ├── run-all.bat          ← 백엔드+프론트엔드 동시 실행
│   ├── docker-deploy.bat    ← Docker로 배포
│
├── Docker 관련
│   ├── Dockerfile          
│   ├── docker-compose.yml   ← Perplexity API 키 추가
│   └── .env                 ← Docker용 환경 변수
│
├── Backend (백엔드)
│   └── backend/
│       ├── .env             ← API 키 설정 (핵심!)
│       ├── pyproject.toml   ← httpx 의존성 추가
│       └── src/
│           ├── agent/
│           │   ├── app.py       ← FastAPI 서버 
│           │   ├── graph.py     ← LangGraph 워크플로우 
│           │   └── state.py     ← ResearchState 추가
│           └── tools/
│               └── perplexity.py ← Perplexity 검색 도구 
│
└── Frontend (프론트엔드)
    └── frontend/
        └── src/
            └── App.tsx      ← React 컴포넌트
```
<br/><br/>
        
(3) 백엔드 핵심 파일 설명   
[backend/.env] - Gemini API와 Perplexity API를 사용하기 위한 인증 키   
```txt
GEMINI_API_KEY=실제 제미나이 API 키 기입   
PERPLEXITY_API_KEY=실제 퍼플렉시티 API 키 기입   
HOST=0.0.0.0   
PORT=8000
```

[backend/src/tools/perplexity.py] - 사용자 질문을 받아 퍼플렉시티 API를 호출해 웹 검색 실행   
```txt
@tool
async def perplexity_search(query: str, search_recency: str) -> dict:   
"""Perplexity API로 최신 웹 정보를 검색합니다"""
```  

[backend/src/agent/state.py] - 워크플로우 전체에서 사용하는 상태 구조 정의   
```txt
class ResearchState(TypedDict):   
messages: list[BaseMessage]    # 대화 기록 (MemorySaver가 저장)   
query: str                     # 사용자 질문   
search_results: list[dict]     # Perplexity 검색 결과 누적   
citations: list[str]           # 출처 URL 목록   
related_questions: list[str]   # 관련 질문   
analysis: str                  # Gemini 분석 결과   
final_answer: str              # 최종 답변   
iteration: int                 # 검색 횟수 (최대 3회)   
needs_more_research: bool      # 재검색 필요 여부   
- 각 노드가 이 State를 읽고 수정하며 전달   
- MemorySaver가 messages 필드를 세션별로 저장
```
   
**[backend/src/agent/graph.py]** - LangGraph 워크플로우 정의 (핵심 로직)   
```txt
흐름: extract_query → search_perplexity → analyze_with_gemini   
→ should_continue → (재검색 or generate_final_answer)
```
   
1. extract_query: 질문 추출 및 State 초기화   
2. search_perplexity: Perplexity로 웹 검색, 결과 누적   
3. analyze_with_gemini: Gemini가 "정보 충분한가?" 판단   
4. should_continue: 조건 분기 (재검색 vs 답변 생성)   
5. generate_final_answer: 모든 검색 결과 종합하여 최종 답변 생성   
6. MemorySaver: 대화 기록을 RAM에 저장 (세션별, 휘발성)   
   
[backend/src/agent/app.py] - FastAPI 서버 및 API 엔드포인트      
```txt
@app.post("/api/research")   
async def research(request: QueryRequest):   
    # 1. 세션 ID 확인/생성   
    # 2. LangGraph 워크플로우 실행   
    # 3. 결과 반환 (answer, citations, related_questions, iterations)
```
             
1. 프론트엔드에서 POST 요청 받음   
2. session_id로 MemorySaver에서 이전 대화 로드   
3. 워크플로우 실행 후 JSON 응답   
4. CORS 설정으로 프론트엔드(5173) 접근 허용   
<br/>

(4) 그 다음 YAML 내용을 아래와 같이 기입한다.    
"request_url" 부분은 Cloud Run 함수 URL을 기입해준다.    

```json
{
    "display_information": {
        "name": "arabot"
    },
    "features": {
        "bot_user": {
            "display_name": "arabot",
            "always_online": true
        }
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "app_mentions:read",
                "chat:write",
                "channels:history",
                "im:read",
                "im:history"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "request_url": "https://temp.url/slack/events",
            "bot_events": [
                "app_mention",
                "message.im"
            ]
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```
<img width="1600" height="900" alt="image6" src="https://github.com/user-attachments/assets/58173b50-0999-407d-b77f-84a8ae7f70e2" />
<br/><br/>
   
(5) 슬랙봇이 생성되면 "OAuth & Permissions" 항목에 들어가서 OAuth Tokens을 인스톨한다.      
이때 "Bot User OAuth Token"이 생성되는데 메모장 등에 복사해둔다.      
<img width="1600" height="900" alt="image7" src="https://github.com/user-attachments/assets/f4498554-9a55-4a7d-b568-098a2fbad7e9" />
<br/>

(6) 다음은 "Basic Information" 항목에 들어가서 Signing Secret을 확인하고 메모장에 복사해둔다.     
<img width="600" height="800" alt="image8" src="https://github.com/user-attachments/assets/007c541a-0f4d-48ac-90b6-e6a4d1a4260e" />
<br/>

(7) 다음은 슬랙에서 채널 ID를 확인하고 메모장에 복사해둔다.     
<img width="400" height="600" alt="image9" src="https://github.com/user-attachments/assets/96fd4033-8e89-4ac9-a9ec-a915bfac82aa" />   
<img width="500" height="600" alt="image10" src="https://github.com/user-attachments/assets/00ae756b-a3de-4c48-9d55-1859f9653108" />
<br/>

(8) 지금까지 메모장에 복사해넣은 정보를 함수 코드 내용에 맞게 환경변수로 등록한다.
<img width="700" height="600" alt="image11" src="https://github.com/user-attachments/assets/7aa75665-e8d1-4081-b0c6-1b5348287a06" />
<br/><br/>

함수까지 전부 작성이 끝났으면 리소스 생성 절차는 다 끝난 것이다.   
이제 남은 건 Cloud Run 함수와 Slack을 연동해주는 작업뿐이다.   
<br/>

(9) Slack API 웹페이지로 돌아간 뒤 "Event Subscriptions" 항목을 선택한다.       
"Request URL"에 Cloud Run 함수 URL을 기입한다.      
Cloud Run 함수의 여러 탭 중에서 YAML 탭을 보면 함수 URL을 확인할 수 있다.       
그 뒤, 'Verified'라는 녹색 체크가 뜨면 맨 하단의 "Save Changes" 버튼을 클릭한다.           
<img width="900" height="800" alt="image12" src="https://github.com/user-attachments/assets/1f5e4923-20dc-41b9-8fd9-f4cd965dafee" />
<br/>

(10) 이제 Slack에서 테스트만 하면 된다.      
"@봇이름"으로 AI봇을 호출한 뒤 지시를 내려본다.      
만약 봇이 채널에 없다는 메시지가 나타나면 'Add Them' 버튼을 눌러 봇을 채널에 초대한다.         
<img width="800" height="400" alt="image13" src="https://github.com/user-attachments/assets/d2a77fba-e41b-4297-8a58-7104c52e6810" />
<br/>

(11) 채널에 봇이 추가되면 다시 "@봇이름"으로 AI봇을 호출한 뒤 지시를 내려본다.      
뉴스나 블로그 메시지에 "답장" 형태로 지시를 내리면 개별 분석을 더 잘해준다.              
<img width="1800" height="800" alt="image14" src="https://github.com/user-attachments/assets/0630eef5-7a6d-49d6-bb8a-575748d19610" />
<br/>

(12) 일상적인 질문에도 잘 대답해주니 여러 가지 질문으로 테스트 해보도록 한다.           
<img width="1800" height="600" alt="image15" src="https://github.com/user-attachments/assets/3cfff26b-3169-4849-b312-9e093c21fd56" />
<br/>




