#!/usr/bin/env python3
"""Generate date-organized digest files from collected article data."""
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "Web記事" / "AI"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# All articles organized by date
ARTICLES = {
    "2026-04-17": [
        {
            "title": "arXiv注目論文：Autogenesis — 自己進化型エージェントプロトコル",
            "subtitle": "Autogenesis: A Self-Evolving Agent Protocol",
            "source": "arXiv (cs.AI)",
            "url": "https://arxiv.org/abs/2604.15034",
            "published": "2026-04-17",
            "importance": 3,
            "summary": "2026年4月17日、arXivにて自己進化型エージェントの新プロトコル「Autogenesis」が発表された。エージェントが自身のアーキテクチャと行動ポリシーを自律的に修正・進化させるフレームワークで、外部からの再訓練やファインチューニングなしに環境変化に適応する。",
            "bullets": [
                "エージェントが自律的にアーキテクチャと行動ポリシーを自己修正",
                "外部からの再訓練なしに環境変化に適応するプロトコル",
                "自己進化型AIの安全性と制御可能性に関する議論を提起"
            ],
            "tags": "arxiv, self-evolving, agents, protocol, autonomy"
        },
        {
            "title": "arXiv注目論文：LLM Judge信頼性の診断 — Conformal Prediction Sets",
            "subtitle": "Diagnosing LLM Judge Reliability: Conformal Prediction Sets and Transitivity Violations",
            "source": "arXiv (cs.AI)",
            "url": "https://arxiv.org/abs/2604.15302",
            "published": "2026-04-17",
            "importance": 3,
            "summary": "2026年4月17日、LLMを評価者として使用する際の信頼性を診断する新手法が発表された。Conformal Prediction Setsと推移性違反の検出を組み合わせ、LLM Judgeの判定がどの程度信頼できるかを統計的に定量化する。",
            "bullets": [
                "LLM Judgeの信頼性をConformal Prediction Setsで統計的に定量化",
                "推移性違反（A>B, B>C なのに C>A）の検出で矛盾を可視化",
                "LLM-as-a-Judge評価パラダイムの品質保証に貢献"
            ],
            "tags": "arxiv, llm-judge, evaluation, conformal-prediction, reliability"
        },
        {
            "title": "arXiv注目論文：OpenMobile — タスク・軌跡合成によるオープンモバイルエージェント",
            "subtitle": "OpenMobile: Building Open Mobile Agents with Task and Trajectory Synthesis",
            "source": "arXiv (cs.AI)",
            "url": "https://arxiv.org/abs/2604.15093",
            "published": "2026-04-17",
            "importance": 3,
            "summary": "2026年4月17日、モバイルデバイス上で動作するオープンなAIエージェント構築フレームワーク「OpenMobile」が発表された。タスクと操作軌跡の合成データ生成により、スマートフォン操作を自律的に実行するエージェントの訓練を効率化する。",
            "bullets": [
                "モバイルデバイス操作を自律実行するオープンエージェントフレームワーク",
                "タスクと操作軌跡の合成データ生成で訓練を効率化",
                "スマートフォン上のアプリ操作を自動化する実用的アプローチ"
            ],
            "tags": "arxiv, mobile-agents, task-synthesis, automation, open-source"
        },
    ],
    "2026-04-16": [
        {
            "title": "Anthropic、Claude Opus 4.7を発表 — コーディング13%向上＆高解像度ビジョン搭載",
            "subtitle": "Introducing Claude Opus 4.7",
            "source": "Anthropic Blog",
            "url": "https://www.anthropic.com/news/claude-opus-4-7",
            "published": "2026-04-16",
            "importance": 5,
            "summary": "2026年4月16日、AnthropicはClaude Opus 4.7を発表した。コーディングベンチマークで13%向上し、本番タスク解決数はOpus 4.6の3倍に達する。Claude初の高解像度ビジョン対応で最大3.75メガピクセル（従来の1.15MPから約3倍）をサポート。新たな「xhigh」努力レベルを追加し、推論品質とレイテンシのトレードオフをより細かく制御可能に。サイバーセキュリティ能力はMythos Previewから意図的に抑制され、禁止用途の自動検出・ブロック機能を搭載。価格は据え置き（入力$5/M、出力$25/M）。",
            "bullets": [
                "コーディング13%向上、本番タスク解決数がOpus 4.6の3倍",
                "Claude初の高解像度ビジョン：最大3.75MP（従来比3倍）",
                "新「xhigh」努力レベル追加、価格据え置き$5/$25/Mトークン"
            ],
            "tags": "anthropic, claude, opus, vision, coding"
        },
    ],
    "2026-04-15": [
        {
            "title": "OpenAI、Agents SDKの次世代版を発表 — エンタープライズ向けサンドボックス＆100+モデル対応",
            "subtitle": "The next evolution of the Agents SDK",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/the-next-evolution-of-the-agents-sdk/",
            "published": "2026-04-15",
            "importance": 5,
            "summary": "2026年4月15日、OpenAIはAgents SDKの大幅アップデートを発表した。エンタープライズ向けサンドボックス機能により、エージェントは隔離されたワークスペース内で動作し、指定されたファイルやコードにのみアクセス可能。Blaxel、Cloudflare、Vercelなどのサンドボックスプロバイダーと統合し、Manifest抽象化でポータブルなワークスペース記述を実現。100以上のLLMをプロバイダー非依存で利用可能。",
            "bullets": [
                "エンタープライズ向けサンドボックス、Blaxel・Cloudflare・Vercelと統合",
                "100以上のLLMをプロバイダー非依存で利用可能に",
                "Long-Horizonハーネスで構成可能なメモリとファイルシステムツールを提供"
            ],
            "tags": "openai, agents-sdk, sandbox, enterprise, multi-llm"
        },
        {
            "title": "Google、Gemini 3 Flashを一般提供開始 — フロンティア知能を低コストで実現",
            "subtitle": "Gemini 3 Flash: frontier intelligence built for speed",
            "source": "Google DeepMind Blog",
            "url": "https://blog.google/products/gemini/gemini-3-flash",
            "published": "2026-04-15",
            "importance": 4,
            "summary": "2026年4月15日、GoogleはGemini 3 Flashの一般提供開始とベンチマーク・グローバル展開の詳細を公開した。GPQA Diamond（博士レベル推論）で90.4%、Humanity's Last Examで33.7%を達成。価格は入力$0.50/M・出力$3.00/Mトークン、100万トークンのコンテキストウィンドウ対応。秒間156トークンのスループット。",
            "bullets": [
                "GPQA Diamond 90.4%、Humanity's Last Exam 33.7%でフロンティアモデルに匹敵",
                "入力$0.50/M、出力$3.00/Mトークンの低コスト、100万トークンコンテキスト",
                "秒間156トークン、マルチモーダル対応、思考レベルの段階的設定が可能"
            ],
            "tags": "google, gemini, benchmark, multimodal, pricing"
        },
        {
            "title": "Google、Gemini 3.1 Flash TTS発表 — 200+音声タグで次世代AI音声合成",
            "subtitle": "Gemini 3.1 Flash TTS: the next generation of expressive AI speech",
            "source": "Google DeepMind Blog",
            "url": "https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-flash-tts/",
            "published": "2026-04-15",
            "importance": 4,
            "summary": "2026年4月15日、GoogleはGemini 3.1 Flash TTSを発表した。200以上の音声タグでボーカルスタイル・ペース・配信を細かく制御可能なテキスト音声合成モデル。70以上の言語をサポートし、ネイティブなマルチスピーカー対話に対応。Elo 1,211を達成。出力にはSynthID電子透かしが自動付与される。",
            "bullets": [
                "200+音声タグでボーカルスタイル・ペース・配信を細かく制御",
                "70+言語対応、ネイティブマルチスピーカー対話、Elo 1,211達成",
                "入力$1.00/M、音声出力$20.00/M（バッチ50%割引）、SynthID透かし付き"
            ],
            "tags": "google, gemini, tts, speech-synthesis, multilingual"
        },
        {
            "title": "MIT Technology Review「AI時代のプライバシー主導型UX」— 信頼構築のデザイン哲学",
            "subtitle": "Building trust in the AI era with privacy-led UX",
            "source": "MIT Technology Review",
            "url": "https://www.technologyreview.com/2026/04/15/1135530/building-trust-in-the-ai-era-with-privacy-led-ux/",
            "published": "2026-04-15",
            "importance": 3,
            "summary": "2026年4月15日、MIT Technology Reviewはプライバシー主導型UXをAI時代の信頼構築に不可欠なデザイン哲学として紹介した。データ収集・利用に関する透明性を顧客関係の中核に据えるアプローチ。",
            "bullets": [
                "プライバシー主導型UXをAI時代の信頼構築の中核デザイン哲学として提唱",
                "データ収集の透明性と同意管理を設計段階から組み込むアプローチ",
                "AI普及に伴うプライバシー懸念への実践的フレームワーク"
            ],
            "tags": "privacy, ux-design, trust, ai-ethics, transparency"
        },
    ],
    "2026-04-14": [
        {
            "title": "OpenAI、Axiosサプライチェーン攻撃への対応を公開 — 北朝鮮ハッカー集団が関与",
            "subtitle": "Our response to the Axios developer tool compromise",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/axios-developer-tool-compromise/",
            "published": "2026-04-14",
            "importance": 5,
            "summary": "2026年4月14日、OpenAIはAxios npmライブラリのサプライチェーン攻撃への対応を公開した。3月31日にAxiosが侵害され、OpenAIのGitHub ActionsワークフローがmacOSアプリ署名時に悪意あるバージョンを実行。原因はピン留めされたコミットハッシュではなくフローティングタグを使用していた設定ミス。ユーザーデータへのアクセスやシステム侵害はなし。Googleの調査により北朝鮮のLazarus Groupによる攻撃と判明。OpenAIは5月8日にmacOSコード署名証明書を失効させ、全macOSユーザーにアプリ更新を求めている。",
            "bullets": [
                "Axios npmライブラリのサプライチェーン攻撃、北朝鮮Lazarus Groupが関与",
                "ユーザーデータ・システムへの侵害はなし、マルウェア署名も検出されず",
                "5月8日にmacOS署名証明書を失効、全ユーザーにアプリ更新を要請"
            ],
            "tags": "openai, security, supply-chain, axios, lazarus-group"
        },
        {
            "title": "Anthropic、Novartis CEOのVas Narasimhan氏を取締役に任命 — Trust指名取締役が過半数に",
            "subtitle": "Anthropic's Long-Term Benefit Trust appoints Vas Narasimhan to the Board of Directors",
            "source": "Anthropic Blog",
            "url": "https://www.anthropic.com/news/narasimhan-board",
            "published": "2026-04-14",
            "importance": 4,
            "summary": "2026年4月14日、AnthropicのLong-Term Benefit TrustはNovartis CEOのVas Narasimhan氏を取締役に任命した。製薬業界から初のAIスタートアップ取締役就任で、35以上の新薬の開発・承認を統括した経験を持つ。Trust指名取締役が過半数を占めることに。",
            "bullets": [
                "Novartis CEO Vas Narasimhan氏が取締役就任、製薬業界から初のAIボード参画",
                "Trust指名の取締役が過半数に、公益ミッション優先のガバナンス強化",
                "Dario Amodei、Reed Hastingsらと共に取締役会を構成"
            ],
            "tags": "anthropic, governance, board, novartis, public-benefit"
        },
        {
            "title": "Google DeepMind、Gemini Robotics ER 1.6を発表 — ロボットの推論能力が劇的向上",
            "subtitle": "Gemini Robotics-ER 1.6: Enhanced Embodied Reasoning",
            "source": "Google DeepMind Blog",
            "url": "https://deepmind.google/blog/gemini-robotics-er-1-6/",
            "published": "2026-04-14",
            "importance": 5,
            "summary": "2026年4月14日、Google DeepMindはロボット向けAIモデル「Gemini Robotics ER 1.6」を発表した。計器読み取りで93%の成功率（ER 1.5は23%）。エージェンティック・ビジョンで視覚推論とコード実行を統合。Gemini APIとGoogle AI Studioから利用可能。",
            "bullets": [
                "計器読み取り成功率93%（ER 1.5比で4倍、Gemini 3.0 Flash比で1.4倍）",
                "エージェンティック・ビジョンで視覚推論とコード実行を統合",
                "マルチビュー理解と安全性ポリシー準拠度の大幅改善"
            ],
            "tags": "deepmind, robotics, gemini, embodied-reasoning, spatial-ai"
        },
        {
            "title": "MIT Technology Review「AIがソフトウェアエンジニアリングの未来を再定義」",
            "subtitle": "Redefining the future of software engineering",
            "source": "MIT Technology Review",
            "url": "https://www.technologyreview.com/2026/04/14/1134397/redefining-the-future-of-software-engineering/",
            "published": "2026-04-14",
            "importance": 4,
            "summary": "2026年4月14日、MIT Technology ReviewはエージェンティックAIがソフトウェアエンジニアリングに第3の変革をもたらしていると報じた。AIエージェントがプロジェクト全体を自律管理する時代へ。",
            "bullets": [
                "AIエージェントが自律的に判断しソフトウェアプロジェクト全体を管理する時代へ",
                "コード補完→コード生成→プロジェクト自律管理への第3の変革",
                "開発者の役割がコーダーからアーキテクト・レビューアーにシフト"
            ],
            "tags": "software-engineering, agentic-ai, coding, automation, developer-tools"
        },
        {
            "title": "MIT Technology Review「10 Things That Matter in AI Right Now」を4月21日に発表予定",
            "subtitle": "Coming soon: 10 Things That Matter in AI Right Now",
            "source": "MIT Technology Review",
            "url": "https://www.technologyreview.com/2026/04/14/1135298/coming-soon-10-things-that-matter-in-ai-right-now/",
            "published": "2026-04-14",
            "importance": 3,
            "summary": "2026年4月14日、MIT Technology Reviewは初の年間AIリスト「10 Things That Matter in AI Right Now」を4月21日のEmTech AIカンファレンスで発表すると予告。",
            "bullets": [
                "初の年間AIリスト「10 Things That Matter in AI Right Now」を4月21日に発表",
                "AIコンパニオン・解釈性・生成コーディング・ハイパースケールDCが候補",
                "EmTech AI 2026で「The Great Integration」をテーマに実務導入を議論"
            ],
            "tags": "mit-tech-review, emtech, ai-trends, interpretability, data-centers"
        },
        {
            "title": "Frontier-Eng — 実世界エンジニアリングタスクで自己進化エージェントをベンチマーク",
            "subtitle": "Frontier-Eng: Benchmarking Self-Evolving Agents on Real-World Engineering Tasks",
            "source": "arXiv (cs.AI)",
            "url": "https://arxiv.org/abs/2604.12290",
            "published": "2026-04-14",
            "importance": 3,
            "summary": "2026年4月14日、5カテゴリ47タスクの実世界エンジニアリングベンチマーク「Frontier-Eng」が発表された。物理シミュレータやFEMソルバーなど産業グレードの検証器を使用。Claude 4.6 Opusが最も安定した性能。",
            "bullets": [
                "5カテゴリ47タスクの実世界エンジニアリングベンチマーク",
                "物理シミュレータ・FEMソルバーなど産業グレードの検証器を使用",
                "Claude 4.6 Opusが最も安定した性能、ただし全モデルに挑戦的"
            ],
            "tags": "arxiv, benchmark, agents, engineering, optimization"
        },
    ],
    "2026-04-13": [
        {
            "title": "MIT Technology Review「AI Indexで見る2026年のAI最前線」— Anthropicがリード",
            "subtitle": "Want to understand the current state of AI? Check out these charts",
            "source": "MIT Technology Review",
            "url": "https://www.technologyreview.com/2026/04/13/1135675/want-to-understand-the-current-state-of-ai-check-out-these-charts/",
            "published": "2026-04-13",
            "importance": 4,
            "summary": "2026年4月13日、MIT Technology ReviewはStanford大学HAI発行の「2026 AI Index」の主要チャートを紹介。2026年3月時点でAnthropicがモデル性能ランキングでトップ、xAI・Google・OpenAIが僅差で続く。米中のAI性能はほぼ拮抗。",
            "bullets": [
                "2026年3月時点でAnthropicがAIモデル性能でトップ、xAI・Google・OpenAIが僅差",
                "米中のAI性能はほぼ拮抗状態",
                "Stanford HAIの2026 AI Indexから主要データを抽出・可視化"
            ],
            "tags": "stanford, ai-index, benchmark, ranking, anthropic"
        },
    ],
    "2026-04-08": [
        {
            "title": "OpenAI、Child Safety Blueprintと安全性フェローシップを発表",
            "subtitle": "Introducing the Child Safety Blueprint and OpenAI Safety Fellowship",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/child-safety-blueprint/",
            "published": "2026-04-08",
            "importance": 4,
            "summary": "2026年4月8日、OpenAIはAI企業向けの児童安全対策ガイドライン「Child Safety Blueprint」と、安全性研究を推進する「OpenAI Safety Fellowship」を発表した。業界全体のAI安全基準の引き上げを目指す取り組み。",
            "bullets": [
                "AI企業向け児童安全対策ガイドライン「Child Safety Blueprint」を公開",
                "安全性研究を推進する「OpenAI Safety Fellowship」を設立",
                "業界全体のAI安全基準の引き上げを目指す"
            ],
            "tags": "openai, child-safety, ai-safety, fellowship, guidelines"
        },
        {
            "title": "OpenAI、メディア企業TBPNを買収 — AI企業初のメディア買収",
            "subtitle": "OpenAI acquires TBPN",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/openai-acquires-tbpn/",
            "published": "2026-04-08",
            "importance": 4,
            "summary": "2026年4月8日、OpenAIはテック系ライブトーク番組TBPN（Technology Business Programming Network）を買収した。AI企業によるメディア企業の初買収。TBPNは平日11時〜14時（PT）に放送され、2026年の売上見込みは3,000万ドル超（WSJ報道）。Chris Lehane率いる戦略部門に所属し、編集の独立性は維持される。",
            "bullets": [
                "AI企業によるメディア企業の初買収、TBPNは年間売上3,000万ドル超の見込み",
                "平日11時〜14時放送のテック系ライブトーク番組",
                "編集の独立性を明確に保護、番組内容・ゲスト・編集権はTBPNが維持"
            ],
            "tags": "openai, media, acquisition, tbpn, strategy"
        },
        {
            "title": "Mustafa Suleyman — AI開発は壁にぶつからない、その理由",
            "subtitle": "Mustafa Suleyman: AI development won't hit a wall anytime soon",
            "source": "MIT Technology Review",
            "url": "https://www.technologyreview.com/2026/04/08/1135398/mustafa-suleyman-ai-future/",
            "published": "2026-04-08",
            "importance": 3,
            "summary": "2026年4月8日、MIT Technology ReviewはMicrosoft AI CEOのMustafa Suleyman氏のインタビューを掲載。フロンティアAIモデルの訓練データは2010年から1兆倍に成長（10^14 FLOPsから10^26 FLOPs超）し、AIの壁を予測する懐疑論者は繰り返し誤ってきたと主張。",
            "bullets": [
                "AI訓練の計算量は2010年から1兆倍に成長（10^14→10^26 FLOPs超）",
                "懐疑論者のAI壁予測は繰り返し外れていると指摘",
                "指数関数的な計算能力の成長がAI進化を支え続けると主張"
            ],
            "tags": "microsoft, mustafa-suleyman, ai-scaling, compute, interview"
        },
    ],
    "2026-04-07": [
        {
            "title": "Anthropic、Claude Mythos PreviewとProject Glasswingを発表 — AIサイバーセキュリティの新時代",
            "subtitle": "Assessing Claude Mythos Preview's cybersecurity capabilities",
            "source": "Anthropic Blog",
            "url": "https://red.anthropic.com/2026/mythos-preview/",
            "published": "2026-04-07",
            "importance": 5,
            "summary": "2026年4月7日、Anthropicは新モデル「Claude Mythos Preview」とセキュリティプロジェクト「Project Glasswing」を発表。Firefoxの181件のJavaScript脆弱性を悪用可能なエクスプロイトに変換（Opus 4.6は2件のみ）。AWS・Apple・Google・Microsoft等11社が参画。",
            "bullets": [
                "Firefoxの脆弱性悪用で181件成功、従来のOpus 4.6（2件）を圧倒",
                "FreeBSDの17年間未発見のリモートコード実行脆弱性を自律発見",
                "AWS・Apple・Google・Microsoftなど11社がProject Glasswingに参画"
            ],
            "tags": "anthropic, claude, cybersecurity, zero-day, project-glasswing"
        },
    ],
    "2026-04-06": [
        {
            "title": "Anthropic、GoogleおよびBroadcomとの提携拡大 — 次世代TPUで複数ギガワット確保",
            "subtitle": "Anthropic expands partnership with Google and Broadcom",
            "source": "Anthropic Blog",
            "url": "https://www.anthropic.com/news/google-broadcom-partnership-compute",
            "published": "2026-04-06",
            "importance": 4,
            "summary": "2026年4月6日、AnthropicはGoogleおよびBroadcomとの提携拡大を発表。年間実行売上高は300億ドル突破（2025年末比3倍超）。月間100万ドル超の企業顧客は1,000社超。次世代TPUで「複数ギガワット」規模の計算容量を2027年から確保。",
            "bullets": [
                "年間実行売上高が300億ドル突破、2025年末比で3倍超の成長",
                "月間100万ドル超の企業顧客が1,000社超、2ヶ月で倍増",
                "次世代TPUで「複数ギガワット」規模の計算容量を2027年から確保"
            ],
            "tags": "anthropic, google, broadcom, tpu, infrastructure"
        },
        {
            "title": "AIが小規模オンライン販売を変革 — Alibaba Accioが月間1,000万ユーザー突破",
            "subtitle": "AI is changing how small online sellers decide what to make",
            "source": "MIT Technology Review",
            "url": "https://www.technologyreview.com/2026/04/06/1135118/ai-online-seller-alibaba-accio/",
            "published": "2026-04-06",
            "importance": 3,
            "summary": "2026年4月6日、MIT Technology ReviewはAlibabaのAIソーシングツール「Accio」がオンライン販売を変革している実態を報じた。2024年ローンチから2026年3月に月間1,000万アクティブユーザー突破。Accio Workは30分でアイデアから店舗開設まで完了。",
            "bullets": [
                "2024年ローンチから急成長、2026年3月に月間1,000万アクティブユーザー突破",
                "Alibabaユーザーの5人に1人がAIに商品調達を相談",
                "Accio Workは30分でアイデアから店舗開設・出品まで完了するAIエージェント"
            ],
            "tags": "alibaba, accio, e-commerce, ai-agent, sourcing"
        },
    ],
    "2026-04-02": [
        {
            "title": "OpenAI、史上最大の1,220億ドル資金調達を完了 — 企業価値8,520億ドル",
            "subtitle": "OpenAI raises $122 billion to accelerate the next phase of AI",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/accelerating-the-next-phase-ai/",
            "published": "2026-04-02",
            "importance": 5,
            "summary": "2026年4月2日、OpenAIは史上最大規模の1,220億ドルの資金調達を完了。企業価値8,520億ドル。Amazon・NVIDIA・SoftBankが主導。初の個人投資家参加で30億ドル超調達。月間売上20億ドル、年間売上131億ドルだが赤字経営。",
            "bullets": [
                "企業価値8,520億ドル、1,220億ドルの史上最大資金調達ラウンドを完了",
                "SoftBank・Amazon・NVIDIAが主導、初の個人投資家参加で30億ドル超を調達",
                "月間売上20億ドル・年間売上131億ドルだが依然赤字経営"
            ],
            "tags": "openai, funding, valuation, softbank, nvidia"
        },
        {
            "title": "Google DeepMind、Gemma 4を公開 — 最も高性能なオープンモデル",
            "subtitle": "Gemma 4: Byte for byte, the most capable open models",
            "source": "Google DeepMind Blog",
            "url": "https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/",
            "published": "2026-04-02",
            "importance": 4,
            "summary": "2026年4月2日、Google DeepMindはオープンモデル「Gemma 4」をApache 2.0ライセンスで公開。高度な推論とエージェントワークフロー向けに特化設計。デバイス上で自律行動・オフラインコード生成が可能。",
            "bullets": [
                "Apache 2.0ライセンスで公開、「バイト単位で最も高性能なオープンモデル」",
                "高度な推論・エージェントワークフロー・マルチステップ計画に特化",
                "デバイス上で自律行動・オフラインコード生成・音声視覚処理が可能"
            ],
            "tags": "google, gemma, open-source, agents, edge-ai"
        },
        {
            "title": "OpenAI、エンタープライズAIの次のフェーズを発表 — 売上の40%超が企業向け",
            "subtitle": "The next phase of enterprise AI",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/next-phase-of-enterprise-ai/",
            "published": "2026-04-02",
            "importance": 4,
            "summary": "2026年4月2日、OpenAIはエンタープライズAI戦略の新フェーズを発表。企業向け売上が全体の40%超。ChatGPT週間9億ユーザー。AWSと共同でStateful Runtime Environmentを構築中。",
            "bullets": [
                "エンタープライズ売上が全体の40%超、2026年末にはコンシューマーと同等へ",
                "ChatGPTの週間アクティブユーザーが9億人に到達",
                "AWSと共同でエージェント向け「Stateful Runtime Environment」を構築中"
            ],
            "tags": "openai, enterprise, chatgpt, agents, aws"
        },
    ],
    "2026-04-01": [
        {
            "title": "ギグワーカーが自宅でヒューマノイドロボットを訓練する新経済圏",
            "subtitle": "The gig workers who are training humanoid robots at home",
            "source": "MIT Technology Review",
            "url": "https://www.technologyreview.com/2026/04/01/1134863/humanoid-data-training-gig-economy-2026-breakthrough-technology/",
            "published": "2026-04-01",
            "importance": 4,
            "summary": "2026年4月1日、MIT Technology Reviewはヒューマノイドロボット訓練の新データ収集手法を報じた。Micro1社は71カ国から約4,000人を雇用しiPhoneで家事動画を収集。月間16万時間超。Tesla・Figure AI等が購入。",
            "bullets": [
                "71カ国4,000人のギグワーカーがiPhoneで月間16万時間超の家事動画を収集",
                "Tesla・Figure AI・Agility Roboticsなどが訓練データとして購入",
                "2025年のヒューマノイドロボット投資額は60億ドル超、データ購入に年間1億ドル以上"
            ],
            "tags": "humanoid-robots, gig-economy, data-collection, training, micro1"
        },
    ],
    "2026-03-31": [
        {
            "title": "オーストラリア政府とAnthropic、AI安全性・研究でMOUを締結",
            "subtitle": "Australian government and Anthropic sign MOU for AI safety and research",
            "source": "Anthropic Blog",
            "url": "https://www.anthropic.com/news/australia-MOU",
            "published": "2026-03-31",
            "importance": 3,
            "summary": "2026年3月31日、AnthropicのCEO Dario Amodei氏がキャンベラでAlbanese首相と会談し、オーストラリアの国家AIプラン初の取り決めとなるMOUを締結。Anthropic Economic Indexデータを豪政府に共有し、天然資源・農業・医療・金融サービスに焦点。豪研究機関との300万豪ドルの研究提携も発表。",
            "bullets": [
                "オーストラリア国家AIプラン初の取り決め、Dario Amodei氏がAlbanese首相と会談",
                "Anthropic Economic Indexデータを豪政府に共有、4分野に焦点",
                "300万豪ドルの研究提携、疾病診断とCS教育に投資"
            ],
            "tags": "anthropic, australia, government, mou, ai-safety"
        },
    ],
    "2026-03-26": [
        {
            "title": "Google、Gemini 3.1 Flash Liveを発表 — リアルタイムマルチモーダル音声AI",
            "subtitle": "Gemini 3.1 Flash Live: Making audio AI more natural and reliable",
            "source": "Google DeepMind Blog",
            "url": "https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-flash-live/",
            "published": "2026-03-26",
            "importance": 4,
            "summary": "2026年3月26日、GoogleはGemini 3.1 Flash Liveを発表。リアルタイムのマルチモーダル音声モデルで、音声・画像・動画・テキストを処理。90以上の言語に対応し、初回応答までの時間は960msのサブ秒。ComplexFuncBench Audioで90.8%（前世代比約20%向上）。200以上の国と地域で利用可能。",
            "bullets": [
                "音声・画像・動画・テキストのリアルタイムマルチモーダル処理、90+言語対応",
                "初回応答960msのサブ秒、ComplexFuncBench Audio 90.8%（前世代比+20%）",
                "Google Search Live・Gemini Live（200+国）で利用可能"
            ],
            "tags": "google, gemini, voice-ai, multimodal, real-time"
        },
        {
            "title": "Google DeepMind、AI操作から人々を守るツールキットを発表",
            "subtitle": "Protecting people from harmful manipulation",
            "source": "Google DeepMind Blog",
            "url": "https://deepmind.google/blog/protecting-people-from-harmful-manipulation/",
            "published": "2026-03-26",
            "importance": 3,
            "summary": "2026年3月26日、Google DeepMindは現実世界でのAI操作を測定する初の実証済みツールキットを発表。英米印で10,000人超が参加した9つの研究に基づく。金融（投資シナリオ）と健康（サプリメント選択）の高リスク領域で検証し、健康関連トピックではAIの操作が最も効果が低いことが判明。",
            "bullets": [
                "現実世界でのAI操作を測定する初の実証済みツールキット",
                "英米印で10,000人超が参加した9つの研究に基づく",
                "健康関連トピックではAIの操作効果が最も低いことが判明"
            ],
            "tags": "deepmind, ai-safety, manipulation, research, ethics"
        },
    ],
    "2026-03-25": [
        {
            "title": "Google、Lyria 3 Proを発表 — 最大3分の楽曲を構造的に生成",
            "subtitle": "Lyria 3 Pro: Create longer tracks in more styles",
            "source": "Google DeepMind Blog",
            "url": "https://blog.google/innovation-and-ai/technology/ai/lyria-3-pro/",
            "published": "2026-03-25",
            "importance": 3,
            "summary": "2026年3月25日、GoogleはAI音楽生成モデルLyria 3 Proを発表。最大3分の楽曲生成が可能（Lyria 3は30秒）。イントロ・バース・コーラス・ブリッジなどの楽曲構造を理解。Geminiアプリ（有料）、Google Vids、Vertex AI等で利用可能。全出力にSynthID透かしを付与。",
            "bullets": [
                "最大3分の楽曲生成（Lyria 3の30秒から大幅延長）",
                "イントロ・バース・コーラス・ブリッジなど楽曲構造を理解",
                "Geminiアプリ・Vertex AI・AI Studioで提供、SynthID透かし付き"
            ],
            "tags": "google, lyria, music-generation, ai-creative, synthid"
        },
    ],
    "2026-03-24": [
        {
            "title": "OpenAI、ChatGPTにビジュアルショッピング体験を導入 — 主要小売7社と連携",
            "subtitle": "Powering Product Discovery in ChatGPT",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/powering-product-discovery-in-chatgpt/",
            "published": "2026-03-24",
            "importance": 3,
            "summary": "2026年3月24日、OpenAIはChatGPTにリッチなビジュアルショッピング体験を導入した。商品の横並び比較、画像アップロードによる類似品検索、会話型絞り込みが可能。Target・Sephora・Nordstrom・Lowe's・Best Buy・Home Depot・Wayfairと提携し、Agentic Commerce Protocol（ACP）を拡張。ChatGPT全プランで利用可能。",
            "bullets": [
                "横並び比較・画像検索・会話型絞り込みのビジュアルショッピング体験",
                "Target・Sephora・Best Buy等7社と連携、ACPを拡張",
                "ChatGPT Free/Go/Plus/Proの全プランで利用可能"
            ],
            "tags": "openai, chatgpt, shopping, e-commerce, acp"
        },
    ],
    "2026-03-19": [
        {
            "title": "OpenAI、PythonツールのAstralを買収 — uv・Ruff開発元がCodexチームに合流",
            "subtitle": "OpenAI to acquire Astral",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/openai-to-acquire-astral/",
            "published": "2026-03-19",
            "importance": 4,
            "summary": "2026年3月19日、OpenAIはPythonツール企業Astralの買収を発表。Astralはuv・Ruff・tyなど数百万の開発者ワークフローを支えるオープンソースツールを開発。AstralチームはCodexグループに合流し、Codexの週間アクティブユーザーは発表時200万人超、月末には300万人超に成長。オープンソース製品は買収後も継続サポート。",
            "bullets": [
                "Python開発ツールuv・Ruff・tyの開発元Astralを買収",
                "Codex週間アクティブユーザー200万人超→300万人超に成長",
                "オープンソース製品は買収後も継続してサポート"
            ],
            "tags": "openai, astral, python, uv, ruff, acquisition"
        },
    ],
    "2026-03-18": [
        {
            "title": "Anthropic「81,000人がAIに何を求めているか」— 大規模調査レポート",
            "subtitle": "What 81,000 people want from AI",
            "source": "Anthropic Blog",
            "url": "https://www.anthropic.com/81k-interviews",
            "published": "2026-03-18",
            "importance": 4,
            "summary": "2026年3月18日、Anthropicは80,508人のClaudeユーザーをAIインタビュアーが調査した大規模レポートを公開。最大の期待は「専門的卓越性」（18.8%）、最大の懸念は「信頼性・ハルシネーション」（26.7%）、次いで雇用喪失（22.3%）、自律性の喪失（21.9%）。67%が全体的にポジティブな感情を表明。「光と影」パターンとして、AIの感情サポートを重視する人はAI依存を恐れる確率も3倍高い。",
            "bullets": [
                "80,508人調査：最大の期待は専門的卓越性（18.8%）、最大の懸念は信頼性（26.7%）",
                "67%がポジティブ、雇用喪失（22.3%）と自律性喪失（21.9%）も上位懸念",
                "AIの感情サポートを重視する人はAI依存を恐れる確率も3倍高い"
            ],
            "tags": "anthropic, survey, user-research, ai-sentiment, 81k"
        },
    ],
    "2026-03-17": [
        {
            "title": "OpenAI、GPT-5.4 miniとnanoを発表 — 最安$0.20/Mトークンのコスト効率モデル",
            "subtitle": "Introducing GPT-5.4 mini and nano",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/introducing-gpt-5-4-mini-and-nano/",
            "published": "2026-03-17",
            "importance": 4,
            "summary": "2026年3月17日、OpenAIはGPT-5.4 miniとnanoを発表。miniは40万トークンコンテキスト、GPT-5 mini比2倍以上高速で$0.75/$4.50/Mトークン。nanoはAPI専用で$0.20/Mの最安モデル、分類・データ抽出・ランキング向けに設計。miniはChatGPT Free/Goで利用可能。",
            "bullets": [
                "GPT-5.4 mini: 40万コンテキスト、GPT-5 mini比2倍高速、$0.75/$4.50/M",
                "GPT-5.4 nano: API専用$0.20/M、分類・データ抽出向け最安モデル",
                "miniはChatGPT Free/Goティアで利用可能"
            ],
            "tags": "openai, gpt-5-4, mini, nano, pricing"
        },
        {
            "title": "Google DeepMind、AGI測定の認知フレームワークと$200K Kaggleハッカソンを発表",
            "subtitle": "Measuring progress toward AGI: A cognitive framework",
            "source": "Google DeepMind Blog",
            "url": "https://blog.google/innovation-and-ai/models-and-research/google-deepmind/measuring-agi-cognitive-framework/",
            "published": "2026-03-17",
            "importance": 4,
            "summary": "2026年3月17日、Google DeepMindは汎用知能を10の認知能力（知覚・生成・注意・学習・記憶・推論・メタ認知・実行機能・問題解決・社会的認知）に分解するフレームワークを発表。評価のギャップ5分野に対し$200KのKaggleハッカソン（4月16日まで、結果6月1日）を開催。各トラック上位2名に$10K、グランプリ4名に$25K。",
            "bullets": [
                "汎用知能を10の認知能力に分解するフレームワークを発表",
                "評価ギャップ5分野に$200KのKaggleハッカソンを開催",
                "各トラック上位2名に$10K、グランプリ4名に$25Kの賞金"
            ],
            "tags": "deepmind, agi, cognitive-framework, kaggle, evaluation"
        },
    ],
    "2026-03-12": [
        {
            "title": "Anthropic、Claude Partner Networkに1億ドル投資を発表",
            "subtitle": "Anthropic invests $100 million into the Claude Partner Network",
            "source": "Anthropic Blog",
            "url": "https://www.anthropic.com/news/claude-partner-network",
            "published": "2026-03-12",
            "importance": 4,
            "summary": "2026年3月12日、Anthropicは2026年のパートナーネットワークに1億ドルの初期投資を発表。パートナー向けチームを5倍に拡大し、Applied AIエンジニア・技術アーキテクト・ローカライズGTMを配備。Claude Certified Architect等の新認定制度を導入。Accenture・Deloitte・PwC・KPMG等が初期パートナー。レガシーコード移行のCode Modernizationスターターキットも提供。",
            "bullets": [
                "2026年パートナーネットワークに1億ドル投資、パートナー向けチーム5倍拡大",
                "Claude Certified Architect等の新認定制度を導入",
                "Accenture・Deloitte・PwC・KPMGが初期パートナー"
            ],
            "tags": "anthropic, partner-network, certification, enterprise, investment"
        },
    ],
    "2026-03-11": [
        {
            "title": "Anthropic、The Anthropic Instituteを設立 — Jack Clarkが公益担当責任者に就任",
            "subtitle": "Introducing The Anthropic Institute",
            "source": "Anthropic Blog",
            "url": "https://www.anthropic.com/news/the-anthropic-institute",
            "published": "2026-03-11",
            "importance": 4,
            "summary": "2026年3月11日、Anthropicは学際的研究機関「The Anthropic Institute」を設立。MLエンジニア・経済学者・社会科学者を擁し、Frontier Red Team・Societal Impacts・Economic Researchの各チームを統合。共同創業者Jack Clarkが公益担当責任者（Head of Public Benefit）に就任。Matt Botvinick氏（元Google DeepMind・Yale法学）をAIと法の研究に、Anton Korinek氏（UVA経済学教授）を変革的AI経済学に採用。",
            "bullets": [
                "学際的研究機関を設立、Frontier Red Team等を統合",
                "共同創業者Jack Clarkが公益担当責任者に就任",
                "AIと法の研究にMatt Botvinick氏、AI経済学にAnton Korinek氏を採用"
            ],
            "tags": "anthropic, institute, jack-clark, public-benefit, research"
        },
    ],
    "2026-03-10": [
        {
            "title": "Anthropic、シドニーをAPAC4番目のオフィスとして開設",
            "subtitle": "Sydney will become Anthropic's fourth office in Asia-Pacific",
            "source": "Anthropic Blog",
            "url": "https://www.anthropic.com/news/sydney-fourth-office-asia-pacific",
            "published": "2026-03-10",
            "importance": 3,
            "summary": "2026年3月10日、Anthropicはシドニーにアジア太平洋地域4番目のオフィスを開設すると発表。東京・ベンガルール・ソウルに続く拠点。Canva・Quantium・Commonwealth Bank of Australiaなどオーストラリア・NZの既存顧客にサービスを強化。長期的な地域インフラの議論も初期段階で進行中。",
            "bullets": [
                "アジア太平洋4番目のオフィス（東京・ベンガルール・ソウルに続く）",
                "Canva・Commonwealth Bank等の既存顧客にサービス強化",
                "長期的な地域インフラの議論も初期段階で進行中"
            ],
            "tags": "anthropic, sydney, apac, expansion, office"
        },
        {
            "title": "Google DeepMind「AlphaGoの10年」— Goから生物学、核融合への軌跡",
            "subtitle": "From games to biology and beyond: 10 years of AlphaGo's impact",
            "source": "Google DeepMind Blog",
            "url": "https://deepmind.google/blog/10-years-of-alphago/",
            "published": "2026-03-10",
            "importance": 3,
            "summary": "2026年3月10日、Google DeepMindはAlphaGoの世界チャンピオン李世ドル氏への勝利から10年を振り返った。有名な「手37」はAIの創造的可能性を示し、実世界の科学問題への応用準備を示唆。AlphaFold 2（2020年）によるタンパク質折りたたみ問題の解決、2億のタンパク質構造のオープンソース化へとつながった。現在は核融合プラズマ封じ込めと電力網最適化のAI研究を推進。",
            "bullets": [
                "AlphaGoの李世ドル戦勝利から10年、「専門家予測より10年早い」達成",
                "AlphaFold 2で2億のタンパク質構造を解明・オープンソース化",
                "現在は核融合プラズマ封じ込めと電力網最適化のAI研究を推進"
            ],
            "tags": "deepmind, alphago, alphafold, nuclear-fusion, anniversary"
        },
    ],
    "2026-03-09": [
        {
            "title": "OpenAI、AIセキュリティ企業Promptfooを買収 — Fortune 500の25%超が利用",
            "subtitle": "OpenAI to acquire Promptfoo",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/openai-to-acquire-promptfoo/",
            "published": "2026-03-09",
            "importance": 4,
            "summary": "2026年3月9日、OpenAIはAIセキュリティ・評価プラットフォームPromptfooの買収を発表。プロンプトインジェクション・脱獄・データ漏洩に対するLLMテストに特化。35万人超の開発者（月間13万人アクティブ）が利用し、Fortune 500の25%超のチームが採用。2024年設立、2,300万ドル調達、直近評価額8,600万ドル。OpenAI Frontierプラットフォームに統合予定、オープンソースは維持。",
            "bullets": [
                "35万人超の開発者が利用、Fortune 500の25%超が採用のAIセキュリティ企業",
                "2024年設立、2,300万ドル調達、評価額8,600万ドル",
                "OpenAI Frontierに統合、オープンソースは維持"
            ],
            "tags": "openai, promptfoo, security, acquisition, evaluation"
        },
    ],
    "2026-03-06": [
        {
            "title": "AnthropicとMozilla提携 — Claude Opus 4.6がFirefoxの22件の脆弱性を発見",
            "subtitle": "Partnering with Mozilla to improve Firefox's security",
            "source": "Anthropic Blog",
            "url": "https://www.anthropic.com/news/mozilla-firefox-security",
            "published": "2026-03-06",
            "importance": 5,
            "summary": "2026年3月6日、AnthropicはMozillaとの提携によるFirefoxセキュリティ改善の成果を発表。Claude Opus 4.6が2026年1月の2週間でFirefoxの22件の新たな脆弱性を発見（14件が高深刻度・7件が中程度・1件が低）。22件のCVEが発行され、全てFirefox 148で修正済み。最初の脆弱性（JSエンジンのUse After Free）はわずか20分で発見。高深刻度バグ数はFirefoxの2025年全高深刻度バグの約1/5に相当。APIクレジット4,000ドルで2件のPoCエクスプロイト（含CVE-2026-2796、CVSS 9.8）に成功。",
            "bullets": [
                "2週間で22件の脆弱性を発見、14件が高深刻度、全てFirefox 148で修正済み",
                "最初の脆弱性をわずか20分で発見（JSエンジンのUse After Free）",
                "APIクレジット$4,000でCVSS 9.8のエクスプロイトに成功"
            ],
            "tags": "anthropic, mozilla, firefox, security, vulnerability"
        },
    ],
    "2026-03-05": [
        {
            "title": "OpenAI、GPT-5.4を発表 — ネイティブPC操作＆100万トークンコンテキスト",
            "subtitle": "Introducing GPT-5.4",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/introducing-gpt-5-4/",
            "published": "2026-03-05",
            "importance": 5,
            "summary": "2026年3月5日、OpenAIは最新フロンティアモデルGPT-5.4を発表。ネイティブなコンピュータ操作機能、100万トークンのコンテキストウィンドウ、新しいツール検索メカニズムを搭載。Codexのデフォルトモデルとして採用され、コーディング・推論・マルチモーダル能力が大幅に向上。",
            "bullets": [
                "ネイティブコンピュータ操作機能を搭載したフロンティアモデル",
                "100万トークンのコンテキストウィンドウ、新しいツール検索メカニズム",
                "Codexのデフォルトモデルとして採用"
            ],
            "tags": "openai, gpt-5-4, computer-use, context-window, frontier"
        },
    ],
    "2026-03-04": [
        {
            "title": "OpenAI、CodexアプリをWindowsで提供開始 — 50万人超が待機リストに",
            "subtitle": "Codex app now available on Windows",
            "source": "OpenAI Blog",
            "url": "https://openai.com/index/introducing-the-codex-app/",
            "published": "2026-03-04",
            "importance": 3,
            "summary": "2026年3月4日、OpenAIはCodexアプリのWindows版を提供開始（macOS版は2月）。Microsoft Store経由で利用可能。複数の並列エージェント、分離されたワークツリー、レビュー可能なdiffをサポートし、セキュリティ用のカスタムネイティブエージェントサンドボックスを搭載。ローンチ前に50万人超が待機リストに登録。3月末にはCodexの週間アクティブユーザーが300万人超に到達。",
            "bullets": [
                "Windows版をMicrosoft Store経由で提供、macOS版に続くリリース",
                "並列エージェント・分離ワークツリー・カスタムサンドボックスを搭載",
                "ローンチ前に50万人超が待機、3月末に週間300万人超に成長"
            ],
            "tags": "openai, codex, windows, ide, developer-tools"
        },
    ],
    "2026-03-03": [
        {
            "title": "Google、Gemini 3.1 Flash-Liteを発表 — 最もコスト効率の高いAIモデル",
            "subtitle": "Gemini 3.1 Flash-Lite: Built for intelligence at scale",
            "source": "Google DeepMind Blog",
            "url": "https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-flash-lite/",
            "published": "2026-03-03",
            "importance": 3,
            "summary": "2026年3月3日、Googleは最もコスト効率の高いAIモデルGemini 3.1 Flash-Liteを発表。入力$0.25/M、出力$1.50/Mトークンの低価格。Gemini 2.5 Flash比で初回応答2.5倍高速、出力45%高速。100万トークンコンテキスト、テキスト・画像・音声・動画のマルチモーダル対応。翻訳・コンテンツモデレーション・UI生成・データ分類など大量処理向けに最適化。",
            "bullets": [
                "入力$0.25/M、出力$1.50/Mの最安クラス、100万トークンコンテキスト",
                "Gemini 2.5 Flash比で初回応答2.5倍高速、出力45%高速",
                "翻訳・モデレーション・UI生成・データ分類など大量処理向けに最適化"
            ],
            "tags": "google, gemini, flash-lite, cost-effective, high-volume"
        },
    ],
    "2026-02-17": [
        {
            "title": "Anthropic、Claude Sonnet 4.6を発表 — 全能力が大幅向上の最強Sonnet",
            "subtitle": "Introducing Claude Sonnet 4.6",
            "source": "Anthropic Blog",
            "url": "https://www.anthropic.com/news/claude-sonnet-4-6",
            "published": "2026-02-17",
            "importance": 5,
            "summary": "2026年2月17日、Anthropicは最も高性能なSonnetモデル「Claude Sonnet 4.6」を発表。コーディング・コンピュータ操作・長文コンテキスト推論・エージェント計画・ナレッジワーク・デザインの全分野で大幅向上。100万トークンコンテキストウィンドウ（ベータ）。早期アクセスの開発者はSonnet 4.6を前モデルより圧倒的に選好し、Opus 4.5（2025年11月）より好まれるケースも多数。価格は$3/$15/Mトークン据え置き。claude.aiとClaude CoworkのFree/Proユーザーのデフォルトモデル。",
            "bullets": [
                "コーディング・コンピュータ操作・推論の全分野で大幅向上した最強Sonnet",
                "100万トークンコンテキスト（ベータ）、Opus 4.5より好まれるケースも",
                "価格$3/$15/M据え置き、Free/Proのデフォルトモデル"
            ],
            "tags": "anthropic, claude, sonnet, coding, computer-use"
        },
    ],
    "2026-02-04": [
        {
            "title": "Anthropic「Claudeは思考するための空間」— 広告なし宣言とサードパーティ統合",
            "subtitle": "Claude is a space to think",
            "source": "Anthropic Blog",
            "url": "https://www.anthropic.com/news/claude-is-a-space-to-think",
            "published": "2026-02-04",
            "importance": 3,
            "summary": "2026年2月4日、AnthropicはClaudeを広告なしの「思考するための空間」として維持することを宣言。広告はClaudeの目的と相容れないと明言。Figma・Asana・Canvaなどのサードパーティツール連携が可能になり、今後も統合先を拡大予定。全てのサードパーティとのやり取りはユーザー起点でなければならず、広告主起点のアクションは許可されない。",
            "bullets": [
                "Claudeを広告なしの「思考するための空間」として維持することを宣言",
                "Figma・Asana・Canva等のサードパーティツール連携が可能に",
                "サードパーティとのやり取りはすべてユーザー起点に限定"
            ],
            "tags": "anthropic, claude, ad-free, integrations, philosophy"
        },
    ],
}


def format_article(idx: int, a: dict) -> str:
    stars = "⭐" * a["importance"]
    bullets_md = "\n".join(f"- {b}" for b in a["bullets"])
    return f"""## {idx}. {a["title"]}
*{a["subtitle"]}*

| Field | Value |
|---|---|
| **Source** | {a["source"]} |
| **URL** | [{a["url"]}]({a["url"]}) |
| **Published** | {a["published"]} |
| **Importance** | {stars} ({a["importance"]}/5) |

{a["summary"]}

{bullets_md}

`Tags:` {a["tags"]}

---
"""


def main():
    total = 0
    for date, articles in sorted(ARTICLES.items(), reverse=True):
        if not articles:
            continue
        out = OUTPUT_DIR / f"{date}.md"
        content = f"""---
date: "{date}"
tags:
  - AI-Digest
sources: {len(set(a["source"] for a in articles))}
---

# AI Daily Digest — {date}

"""
        for i, a in enumerate(articles, 1):
            content += format_article(i, a)

        content += f"\n> Generated at {date} by AI Daily Digest (Claude)\n"
        out.write_text(content, encoding="utf-8")
        print(f"✅ {date}: {len(articles)}件")
        total += len(articles)

    print(f"\n📊 合計: {len(ARTICLES)}日分、{total}件の記事を生成")


if __name__ == "__main__":
    main()
