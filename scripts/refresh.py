from pathlib import Path
import json, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/dashboard-data.json"
TARGET_ARTICLES = 20
NORMAL_MINIMUM = 12
RESTRICTED_MINIMUM = 6

SEARCHES = {
    "material-handling": [
        "warehouse automation", "intralogistics technology", "ASRS market",
        "AMR warehouse", "conveyor automation", "fulfillment technology",
        "material handling outlook", "warehouse robotics investment"
    ],
    "process": [
        "process automation", "industrial instrumentation", "chemical industry outlook",
        "pharmaceutical manufacturing automation", "food processing automation",
        "water wastewater automation", "oil gas digitalization", "process cybersecurity"
    ],
    "heavy-industries": [
        "mining automation", "metals industry automation", "cement plant automation",
        "aggregates equipment technology", "critical minerals investment",
        "autonomous mining", "mining energy efficiency", "metals industry outlook"
    ],
    "manufacturing-assembly": [
        "manufacturing automation", "industrial robotics orders", "machine vision manufacturing",
        "assembly automation", "digital manufacturing", "reshoring factory investment",
        "aerospace manufacturing automation", "automotive manufacturing technology"
    ],
    "packaging": [
        "packaging machinery", "PMMI industry outlook", "packaging robotics",
        "end of line automation", "packaging obsolescence", "packaging changeover",
        "sustainable packaging machinery", "food beverage packaging automation", "consumer packaged goods"
    ],
    "converting-printing-web": [
        "web handling", "roll to roll converting", "printing automation",
        "coating laminating technology", "slitting winding machinery",
        "inline inspection converting", "flexible packaging converting",
        "battery electrode roll to roll", "home personal care"
    ]
}

MODELS = {
    "material-handling": {
        "themes": [("Mixed-fleet orchestration", ["orchestration", "fleet", "amr"]), ("Scalable warehouse robotics", ["robot", "asrs", "automation"]), ("Modular material-flow architecture", ["modular", "conveyor", "material flow"]), ("Lifecycle and software support", ["software", "lifecycle", "maintenance", "service"])],
        "summary": "Warehouse and intralogistics demand is being shaped by fulfillment volumes, labor availability, network redesign and the cost of capital. {signal} Investment remains strongest where modular automation improves throughput, space utilization and service levels without creating excessive integration risk.",
        "brief": ["Material handling customers are balancing renewed automation demand with disciplined project approval. E-commerce, reshoring, production logistics and labor constraints support investment, while interest rates, tariffs and equipment input costs influence timing and scope.", "The strategic shift is from isolated equipment toward an integrated material-flow operating system. Conveyors, AS/RS, robotics, AMRs, controls and warehouse software must share diagnostics, data and lifecycle accountability.", "OEMs and integrators are best positioned when deployment can be phased, operational value can be demonstrated early and a common architecture can scale across sites."],
        "outlook": [("Base case", "Brownfield warehouse automation, controls modernization and phased robotics continue, with customers favoring modular deployments tied to throughput and labor outcomes."), ("Upside", "Lower financing friction, reshoring and stronger logistics volumes accelerate greenfield distribution centers and multi-site programs."), ("Downside", "Tariffs, construction costs or weaker consumer demand defer large systems, while retrofit, software, service and productivity projects remain active.")],
        "economics": "Global material handling economics are influenced by consumer demand, e-commerce volumes, manufacturing reshoring, warehouse construction, interest rates and equipment input costs. North American reindustrialization and foreign direct investment support production logistics; European demand is more sensitive to slower growth and financing; Asian markets benefit from manufacturing scale and automation adoption. Tariffs and steel or aluminum prices can raise system costs, while lower rates can unlock deferred projects. The OEM implication is to emphasize phased capital deployment, space and labor productivity, integration-risk reduction and lifecycle service.",
        "opps": [("Mixed-fleet orchestration", "Coordinate AMRs, conveyors, AS/RS, robotics and warehouse software around shared operational priorities."), ("Modular material-flow architecture", "Use repeatable machine and controls modules to support phased expansion and engineering reuse."), ("Brownfield modernization", "Upgrade installed conveyors, controls, safety and data without requiring total facility replacement."), ("Lifecycle services", "Build recurring value around diagnostics, cybersecurity, obsolescence and system performance.")],
        "takeaway": "Position the OEM ecosystem around scalable, connected and supportable material-flow automation. Lead with throughput, labor, space utilization and uptime, then use robotics, software and AI as enablers of those outcomes."
    },
    "process": {
        "themes": [("Brownfield control modernization", ["brownfield", "modernization", "migration", "dcs"]), ("Industrial AI in process context", ["industrial ai", "analytics", "artificial intelligence"]), ("OT cybersecurity and compliance", ["cyber", "security", "62443", "compliance"]), ("Reliability and operator knowledge", ["reliability", "operator", "workforce", "maintenance"])],
        "summary": "Process investment is being shaped by energy and feedstock costs, global overcapacity, regulation and the operational risk of changing live plants. {signal} Spending favors secure, phased modernization that protects safety, quality and production continuity.",
        "brief": ["Process industries face uneven global conditions. Chemicals contend with soft demand, overcapacity and regional energy-cost differences, while food, pharmaceuticals, water, LNG and utilities create more resilient pockets of demand.", "Customers are modernizing aging controls and connected assets, but shutdown windows, validation requirements and cyber risk constrain the pace. Industrial AI gains credibility when tied to process context, reliability, quality or energy performance.", "OEM differentiation comes from secure migration, standardized skids, useful diagnostics and lifecycle support that reduces startup and production risk."],
        "outlook": [("Base case", "Producers continue phased control migration, cybersecurity, reliability and energy projects during planned outages."), ("Upside", "Improved end-market demand and energy economics accelerate debottlenecking, new process modules and connected asset programs."), ("Downside", "Commodity overcapacity and trade disruption delay capacity projects, while safety, compliance, cybersecurity and obsolescence work remain difficult to defer.")],
        "economics": "Global process economics diverge sharply by region and end market. Chemicals face overcapacity, soft commodity demand and high European energy costs; North America benefits from advantaged energy and LNG investment; Asia remains central to capacity and trade flows. Pharmaceuticals and food are comparatively defensive, while oil, gas and chemicals remain exposed to feedstock prices, geopolitics and trade barriers. Environmental regulation, water scarcity and grid investment create additional demand. OEMs should lead with secure brownfield migration, energy efficiency, reliability and flexible skid architectures rather than assuming broad capacity growth.",
        "opps": [("Secure control migration", "Modernize aging DCS and PLC assets while protecting production continuity and cybersecurity."), ("Connected asset performance", "Combine process, condition and maintenance context around critical equipment."), ("Standardized skid architecture", "Deliver reusable modules with consistent controls, networks, security and diagnostics."), ("Operator enablement", "Use guided workflows, simulation and remote expertise to preserve process knowledge.")],
        "takeaway": "Lead with low-risk modernization that protects production continuity. Connect secure controls, process expertise and lifecycle support to measurable improvements in reliability, quality, energy performance and regulatory confidence."
    },
    "heavy-industries": {
        "themes": [("Critical-mineral supply security", ["critical mineral", "copper", "lithium", "rare earth"]), ("Autonomous and remote operations", ["autonomous", "remote", "automation"]), ("Energy and cost per ton", ["energy", "cost", "ore grade", "productivity"]), ("Reliability and outage execution", ["reliability", "maintenance", "outage", "uptime"])],
        "summary": "Heavy-industry demand is tied to commodity prices, infrastructure, critical-mineral policy, Chinese demand and energy costs. {signal} Long-term supply-security needs support investment, but commodity volatility and long project cycles favor reliability and brownfield work.",
        "brief": ["Mining, metals, cement and bulk-processing markets are supported by infrastructure, electrification and regional supply-security priorities, but opportunity remains uneven by commodity and geography.", "Higher energy costs, declining ore grades, permitting requirements and capital intensity increase the value of automation that improves recovery, throughput, safety and maintenance effectiveness.", "Brownfield debottlenecking, autonomous operations and outage-based modernization generally offer more resilient conversion than broad greenfield capacity."],
        "outlook": [("Base case", "Reliability, debottlenecking, energy efficiency and planned-outage work outpace broad new-capacity investment."), ("Upside", "Critical-mineral policy, infrastructure spending and stronger commodity prices accelerate mines, processing plants and metals capacity."), ("Downside", "Chinese weakness, oversupply or financing pressure delays greenfield projects, while critical-asset and maintenance programs continue.")],
        "economics": "Global heavy-industry economics are driven by commodity prices, Chinese construction and manufacturing demand, infrastructure spending, energy costs, exchange rates and critical-mineral policy. Copper and selected critical minerals benefit from electrification and supply-security investment, while lithium, nickel, iron ore and other markets may face oversupply. Inflation, lower ore grades and energy intensity raise cost per ton. Permitting and geopolitical regionalization lengthen project cycles but also support domestic capacity. OEMs should quantify uptime, recovery, energy per ton and outage execution rather than relying on a generic growth narrative.",
        "opps": [("Autonomous and remote operations", "Improve safety, consistency and access to scarce operating expertise."), ("Critical-asset reliability", "Prioritize conveyors, crushers, mills, kilns, pumps and other production constraints."), ("Energy and power optimization", "Reduce energy per ton and coordinate production with power availability and cost."), ("Outage-based modernization", "Stage controls, drives and network migrations within planned shutdown windows.")],
        "takeaway": "Prioritize reliability, safety and production economics. Position automation around reduced downtime, energy per ton, autonomous operations and staged modernization completed within planned outages."
    },
    "manufacturing-assembly": {
        "themes": [("Flexible robotics for product mix", ["flexible", "robot", "cobot", "high mix"]), ("Vision, quality and traceability", ["vision", "quality", "inspection", "traceability"]), ("Digital engineering and launch speed", ["digital twin", "simulation", "commissioning"]), ("Reshoring and workforce capacity", ["reshoring", "workforce", "labor", "skills"])],
        "summary": "Discrete manufacturing is being shaped by industrial production, machinery orders, automotive and aerospace cycles, reshoring and labor availability. {signal} Flexible robotics, vision and digital engineering remain attractive where they improve quality and product-mix agility.",
        "brief": ["Manufacturing and assembly investment benefits from reindustrialization, aerospace demand, electronics and selected automotive programs, but end-market cycles and tariffs create uneven conditions.", "Customers increasingly favor reusable cells and machine architectures that support multiple products, faster launches and future expansion. Robotics, vision, motion, safety and production data are converging.", "The strongest business cases connect automation to quality, utilization, engineering reuse, labor capacity and commissioning speed."],
        "outlook": [("Base case", "Flexible robotics, vision and digital-engineering projects continue around labor, quality and product-mix requirements."), ("Upside", "Reshoring, aerospace growth and factory expansion accelerate reusable cells, new lines and capacity programs."), ("Downside", "Automotive or machinery weakness slows capacity projects, while quality automation, engineering reuse and targeted labor-saving work persist.")],
        "economics": "Global discrete-manufacturing economics depend on industrial production, machinery orders, automotive and aerospace build rates, electronics cycles, trade policy and foreign direct investment. North American reshoring and defense or aerospace demand support new capacity; European manufacturers face energy and competitiveness pressure; Asian supply chains remain central to electronics and machinery. Tariffs can encourage localization but also raise component and equipment costs. Higher wages and scarce controls or maintenance skills support automation. OEMs should emphasize flexible capacity, engineering reuse, quality and faster launch rather than fixed high-volume assumptions.",
        "opps": [("Flexible robotic cells", "Support mixed-model assembly, tending, material movement and inspection with reusable designs."), ("Integrated motion, safety and vision", "Simplify high-performance architectures and improve machine-level quality."), ("Digital engineering", "Use simulation, emulation and reusable code to reduce design and commissioning time."), ("Quality and traceability", "Connect inspection, genealogy and production context across the line.")],
        "takeaway": "Connect flexible automation to product-mix agility, quality and launch speed. Emphasize reusable machine architectures, integrated robotics and vision, and digital engineering that reduces commissioning time and engineering effort."
    },
    "packaging": {
        "themes": [("Flexible machinery and changeover", ["changeover", "flexible", "sku"]), ("End-of-line robotics and AMRs", ["pallet", "robot", "amr", "end-of-line"]), ("Obsolescence and aftermarket growth", ["obsolescence", "lifecycle", "service"]), ("Material and EPR adaptation", ["recycl", "epr", "material", "sustainability"])],
        "summary": "Packaging demand is influenced by consumer volumes, food and beverage, pharmaceuticals, materials regulation and machinery sourcing. {signal} Flexibility, robotics and lifecycle services remain important as SKU complexity and changing package formats reshape investment.",
        "brief": ["Packaging machinery benefits from relatively defensive food, beverage, pharmaceutical and consumer-goods demand, yet customers face volatile volumes, trade costs and changing package materials.", "The value equation is shifting from peak rated speed toward mix-adjusted throughput, rapid changeover, ease of operation and lifecycle resilience.", "End-of-line robotics, modular machine architecture, obsolescence planning and material flexibility create differentiated OEM opportunities."],
        "outlook": [("Base case", "Flexible machinery, changeover improvement, end-of-line automation and lifecycle programs support steady demand."), ("Upside", "CPG capacity, pharmaceutical investment and package-format changes accelerate new machinery and line modernization."), ("Downside", "Consumer weakness or tariff-driven equipment costs slow new lines, while aftermarket, obsolescence and targeted robotics remain resilient.")],
        "economics": "Global packaging economics are tied to food, beverage, pharmaceutical and consumer-goods volumes, as well as resin, paper, aluminum and energy costs. Demand is comparatively defensive, but regional consumer softness and private-label shifts affect product mix. Tariffs and exchange rates influence imported machinery and components. Material-reduction rules, recycled-content requirements and extended producer responsibility change machine specifications across North America and Europe. Emerging-market consumption supports long-term growth. OEMs should emphasize rapid changeover, material flexibility, total cost of ownership and aftermarket support.",
        "opps": [("Modular machine architecture", "Standardize controls, motion, safety and data for reuse across machine families."), ("Rapid changeover and recipes", "Reduce setup losses and support broader SKU portfolios."), ("End-of-line robotics", "Integrate palletizing, case handling, mobile movement and load stabilization."), ("Obsolescence and aftermarket services", "Use installed-base visibility, conversion kits and proactive lifecycle planning.")],
        "takeaway": "Lead with flexible, operator-friendly packaging systems rather than maximum machine speed alone. Differentiate through rapid changeover, modular architecture, end-of-line integration and proactive lifecycle support."
    },
    "converting-printing-web": {
        "themes": [("Precision web control", ["tension", "registration", "web handling"]), ("Inline inspection and waste reduction", ["inspection", "waste", "yield", "quality"]), ("Workflow and recipe integration", ["workflow", "recipe", "digital"]), ("New substrates and coatings", ["substrate", "coating", "laminating", "battery"])],
        "summary": "Converting and print demand is shaped by packaging volumes, commercial print, substrate costs, run-length compression and specialty roll-to-roll applications. {signal} Precision control and inspection remain defensible because waste and setup directly affect margin.",
        "brief": ["Converting, printing and web-processing markets face shorter runs, customization, substrate variability and pressure to reduce startup waste. Packaging and specialty applications are generally more resilient than traditional commercial print.", "Tension, registration, coating, winding and inspection performance have direct economic value because small process variations can create costly material loss.", "Digital workflow integration and flexible controls help converters manage job complexity, preserve know-how and adapt to emerging roll-to-roll applications."],
        "outlook": [("Base case", "Web control, inspection and workflow automation improve yield and support shorter production runs."), ("Upside", "Flexible packaging, specialty coatings, batteries and advanced roll-to-roll applications expand equipment demand."), ("Downside", "Weak print volumes or high substrate costs slow capacity spending, while waste reduction and precision upgrades remain defensible.")],
        "economics": "Global CPW economics vary by application. Packaging, labels and specialty coatings remain more resilient than commercial print, while advertising and publishing are sensitive to economic growth. Resin, film, foil, paper, ink and energy prices directly affect margins because substrate waste is costly. Shorter runs increase setup frequency and favor automation. Currency and trade conditions shape machinery exports, while sustainability rules accelerate mono-material structures and new coatings. Battery electrodes and flexible electronics create high-value roll-to-roll opportunities. OEMs should quantify yield, startup waste, registration and changeover performance.",
        "opps": [("Precision web control", "Coordinate speed, tension, registration and winding across the full web path."), ("Inline inspection and analytics", "Connect quality findings to process conditions and corrective action."), ("Recipe and workflow integration", "Link job data, setup parameters, quality records and downstream finishing."), ("Controls and drive modernization", "Upgrade aging platforms during planned maintenance while preserving process knowledge.")],
        "takeaway": "Position precision as a measurable business outcome. Lead with tension and registration control, inline quality, reduced startup waste and connected workflows that improve yield across complex substrates and applications."
    }
}

POS = ["growth","expand","increase","investment","record","demand","adoption","recovery","strong","accelerat","opportunity","resilien","productivity"]
NEG = ["decline","slow","risk","shortage","tariff","cost","uncertain","layoff","weak","pressure","delay","volatile","overcapacity"]
TECH = ["automation","robot","ai ","digital","software","vision","autonomous","analytics"]
CAPITAL = ["investment","order","project","capacity","plant","facility","capital"]
WORKFORCE = ["labor","workforce","skills","hiring","operator","talent"]

def normalize_title(value):
    value = re.sub(r"\s+-\s+[^-]{2,50}$", "", value.lower())
    return re.sub(r"[^a-z0-9]+", " ", value).strip()

def parse_date(value):
    try:
        dt = parsedate_to_datetime(value)
        return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None

def fetch_query(query):
    url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(query) + "&hl=en-US&gl=US&ceid=US:en"
    request = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 OEM-Intelligence-Dashboard/3.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())
    output = []
    for item in root.findall(".//item")[:10]:
        title = item.findtext("title", "").strip()
        url = item.findtext("link", "").strip()
        published = item.findtext("pubDate", "").strip()
        source = item.findtext("source", "").strip() or "Google News"
        if title and url:
            output.append({"title":title,"url":url,"published":published,"source":source,"published_dt":parse_date(published)})
    return output

def collect_segment(slug, now):
    raw = []
    successful_queries = 0
    for query in SEARCHES[slug]:
        try:
            raw.extend(fetch_query(query))
            successful_queries += 1
        except Exception as exc:
            print(f"WARNING {slug} query '{query}': {exc}")
    unique = {}
    for item in raw:
        key = normalize_title(item["title"])
        if key and key not in unique:
            unique[key] = item
    articles = list(unique.values())
    articles.sort(key=lambda item: item["published_dt"] or datetime(1970,1,1,tzinfo=timezone.utc), reverse=True)
    recent_90 = [a for a in articles if a["published_dt"] and now-a["published_dt"] <= timedelta(days=90)]
    recent_180 = [a for a in articles if a["published_dt"] and now-a["published_dt"] <= timedelta(days=180)]
    selected = recent_90[:TARGET_ARTICLES]
    if len(selected) < NORMAL_MINIMUM:
        selected = recent_180[:TARGET_ARTICLES]
    if len(selected) < RESTRICTED_MINIMUM:
        selected = articles[:TARGET_ARTICLES]
    publishers = len(set(a["source"] for a in selected))
    for a in selected:
        a.pop("published_dt", None)
    return selected, successful_queries, publishers, len(raw), len(unique)

def hits(text, words): return sum(text.count(word) for word in words)
def clamp(value, low=0, high=100): return max(low, min(high, int(round(value))))
def sentiment_label(score):
    return "Strongly positive" if score>=85 else "Positive" if score>=75 else "Constructive" if score>=65 else "Selectively constructive" if score>=55 else "Mixed" if score>=45 else "Cautious" if score>=30 else "Negative"

def update_segment(slug, segment, articles, searches, publishers, raw_count, unique_count, now):
    model = MODELS[slug]
    text = " ".join(item["title"].lower() for item in articles)
    positive = hits(text, POS); negative = hits(text, NEG); total = max(positive+negative, 1)
    demand = clamp(50+30*(positive-negative)/total, 25, 90)
    technology = clamp(42+5*hits(text, TECH), 25, 92)
    capital = clamp(46+6*hits(text, CAPITAL)-3*hits(text, ["tariff","uncertain","delay"]), 25, 90)
    workforce = clamp(70-7*hits(text, WORKFORCE), 20, 80)
    prior = segment.get("score", 65)
    raw_score = .34*demand+.24*technology+.22*capital+.10*workforce+.10*prior
    movement_cap = 5 if len(articles)>=NORMAL_MINIMUM else 2
    score = clamp(max(prior-movement_cap, min(prior+movement_cap, raw_score)), 25, 95)
    posture = "accelerating" if score>=80 else "disciplined" if score>=65 else "selective" if score>=50 else "cautious"
    signal = f"The current evidence set is {sentiment_label(score).lower()} at {score}, with {('growth signals outweighing constraints' if positive>=negative else 'constraints tempering otherwise durable automation needs')} and a {posture} capital posture."
    ranked = sorted(((hits(text, words), name) for name,words in model["themes"]), reverse=True)
    leaders = [name for _,name in ranked]
    confidence = "Normal" if len(articles)>=NORMAL_MINIMUM else "Limited" if len(articles)>=RESTRICTED_MINIMUM else "Hold prior assessment"
    if len(articles) >= RESTRICTED_MINIMUM:
        segment.update({
            "score":score, "label":sentiment_label(score), "summary":model["summary"].format(signal=signal),
            "leaders":leaders, "brief":[model["brief"][0]+" "+signal, model["brief"][1], model["brief"][2]],
            "outlook":[{"case":a,"text":b} for a,b in model["outlook"]],
            "economics":model["economics"]+f" Current evidence includes {positive} positive-growth references and {negative} constraint references across {len(articles)} selected articles from {publishers} publishers; capital confidence calculates to {capital}.",
            "opportunities":[{"title":a,"text":b} for a,b in model["opps"]],
            "executive_takeaway":model["takeaway"]
        })
        segment["drivers"] = [{"name":"Market demand","score":demand},{"name":"Technology adoption","score":technology},{"name":"Capital confidence","score":capital},{"name":"Workforce availability","score":workforce},{"name":"External risk clarity","score":clamp(65-5*negative,20,80)},{"name":"Strategic resilience","score":clamp(62+4*hits(text,["resilien","regional","secure","lifecycle"]),40,90)}]
    segment["news"] = articles[:5]
    segment["metrics"] = [
        {"label":"Composite sentiment","value":str(segment.get("score",prior)),"note":segment.get("label",sentiment_label(prior))},
        {"label":"Evidence set","value":f"{len(articles)} articles","note":f"{searches} searches · {publishers} publishers"},
        {"label":"Headline signal mix","value":f"{round(100*positive/total)}% positive","note":f"{positive} positive · {negative} constraint references"},
        {"label":"Technology signal","value":str(technology),"note":"Rules-based evidence score"},
        {"label":"Evidence confidence","value":confidence,"note":now.strftime("%B %Y")}
    ]
    segment["evidence_stats"] = {"selected":len(articles),"searches":searches,"publishers":publishers,"raw_results":raw_count,"unique_results":unique_count,"confidence":confidence}
    segment["automation_note"] = "Automatically refreshed from public headline metadata using multiple segment-specific searches, deduplication, date filtering and evidence thresholds. Review before external distribution."

now = datetime.now(timezone.utc)
data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
success = 0
for slug in SEARCHES:
    try:
        articles, searches, publishers, raw_count, unique_count = collect_segment(slug, now)
        if not articles:
            raise RuntimeError("No eligible articles returned")
        update_segment(slug, data["segments"][slug], articles, searches, publishers, raw_count, unique_count, now)
        success += 1
        print(f"{slug}: {len(articles)} selected, {publishers} publishers, {raw_count} raw, {unique_count} unique")
    except Exception as exc:
        print(f"WARNING {slug}: {exc}; retaining last successful segment content")
if success:
    data["last_refreshed"] = now.isoformat().replace("+00:00", "Z")
data["refresh_scope"] = "Multi-query, deduplicated, date-filtered segment refresh with evidence thresholds."
DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print(f"Refreshed {success} of {len(SEARCHES)} segments")
