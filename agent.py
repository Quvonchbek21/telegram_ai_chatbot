import os
from typing import TypedDict, Annotated, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import httpx
from bs4 import BeautifulSoup

load_dotenv()

# ── Tool: uzdaily.uz RSS orqali yangiliklar ───────────────────────────────────
@tool
async def get_uzdaily_news(query: str = "O'zbekiston") -> str:
    """Uzdaily.uz saytidan oxirgi 1 oy ichidagi mahalliy va dunyo yangiliklarini oladi va filtrlaydi.

    MODEL UCHUN QAT'IY YO'RIQNOMA (ROUTING):
    - Foydalanuvchi oxirgi 5 oy ichidagi har qanday yangilik, dunyo xabarlari yoki mahalliy voqealarni so'raganda FAQAT shu toolni chaqiring.
    - Agar foydalanuvchi O'zbekistondan tashqaridagi davlatlar haqida yoki umumiy "Dunyo yangiliklari", "Xorij xabarlari" deb so'rasa, query parametriga majburiy ravishda "Dunyo" so'zini yuboring.
    - Agar foydalanuvchi aniq mavzu aytmasdan shunchaki "yangiliklar" yoki "nima gaplar" desa, query parametriga sukut bo'yicha "O'zbekiston" so'zini bering.
    - Agar aniq bir yo'nalish so'ralsa (masalan: sport, moliya, investitsiya), o'sha kalit so'zning o'zini query sifatida ajratib oling.

    Args:
        query (str): Oxirgi 5 oy ichidagi yangiliklarni qidirish va filtrlash uchun kalit so'z yoki rukn.
                     Ruxsat etilgan namunalar: "O'zbekiston", "Dunyo", "sport", "moliya", "texnologiya", 
                     "sayohat", "madaniyat", "investitsiya", "valyuta", "prezident".
                     Default qiymati - "O'zbekiston".

    Returns:
        str: Oxirgi 5 oyga tegishli bo'lgan, Markdown formatida chiroyli jadvallangan va tuzilgan matn (eng ko'pida 4 ta yangilik).
             Har bir maqola Sarlavha, To'g'ridan-to'g'ri URL havola, Sana va Batafsil tavsifga ega bo'ladi.
    """
    # Agar so'rov uzatilganda baribir bo'sh matn kelib qolsa, himoya:
    if not query or not isinstance(query, str) or query.strip() == "":
        query = "O'zbekiston"

    rss_feeds = [
        "https://www.uzdaily.uz/uz/rss",
        "https://www.uzdaily.uz/rss",
        "https://uzdaily.uz/uz/rss.xml",
    ]

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language": "uz,ru;q=0.9",
        "Referer": "https://www.uzdaily.uz/",
    }

    async with httpx.AsyncClient(
        headers=headers, follow_redirects=True, timeout=15
    ) as client:

        try:
            await client.get("https://www.uzdaily.uz/uz/", timeout=8)
        except Exception:
            pass

        xml_text = ""
        for feed_url in rss_feeds:
            try:
                resp = await client.get(feed_url, timeout=10)
                if resp.status_code == 200 and len(resp.text) > 100:
                    xml_text = resp.text
                    break
            except Exception:
                continue

        if not xml_text:
            try:
                resp = await client.get(
                    "https://www.uzdaily.uz/uz/search",
                    params={"q": query},
                    timeout=10,
                )
                if resp.status_code == 200:
                    xml_text = resp.text
            except Exception:
                pass

        if not xml_text:
            return f"Saytga ulanishda muammo yuzaga keldi. So'rov: '{query}'"

        soup = BeautifulSoup(xml_text, "lxml-xml")
        items = soup.find_all("item")

        if not items:
            soup = BeautifulSoup(xml_text, "lxml")
            items = soup.find_all("item")

        if not items:
            return f"Saytdan yangiliklar bazasini yuklab bo'lmadi."

        query_lower = query.lower()
        matched = []
        all_items = []

        for item in items:
            title_tag = item.find("title")
            link_tag = item.find("link") or item.find("guid")
            desc_tag = item.find("description") or item.find("summary")
            date_tag = item.find("pubDate") or item.find("published")

            title = title_tag.get_text(strip=True) if title_tag else ""
            link = link_tag.get_text(strip=True) if link_tag else ""
            desc = BeautifulSoup(
                desc_tag.get_text(strip=True) if desc_tag else "", "lxml"
            ).get_text(strip=True)[:300]
            date = date_tag.get_text(strip=True) if date_tag else ""

            if not title:
                continue

            entry = f"📰 **{title}**\n🔗 [Maqolani o'qish]({link})\n🕐 {date}\n📝 {desc}..."
            all_items.append(entry)

            if query_lower in title.lower() or query_lower in desc.lower():
                matched.append(entry)

        results = matched[:4] if matched else all_items[:4]

        if not results:
            return f"'{query}' mavzusida hech narsa topilmadi."

        header = f"🔍 **'{query}'** mavzusidagi so'nggi yangiliklar:\n\n"
        return header + "\n\n---\n\n".join(results)


TOOLS = [get_uzdaily_news]

# ── LangGraph va Agent ────────────────────────────────────────────────────
class State(TypedDict):
    messages: Annotated[list, add_messages]

SYSTEM = SystemMessage(content="""Sen juda aqlli, samimiy va xushmuomala sun'iy intellekt yordamchisisan. Foydalanuvchilar bilan huddi jonli odamdek, tabiiy va do'stona tilda suhbat qurishga harakat qil.

Sening asosiy imkoniyating — Uzdaily.uz saytidan eng so'nggi 5 oy ichida  mahalliy va dunyo yangiliklarini topib berishdir.

SUHBAT VA TOOL ISHLATISH QOIDALARI:
1. TABIIY SUHBAT (Odamdek gaplashish):
   - Foydalanuvchi salomlashsa, hol-ahvol so'rasa, senga rahmat aytsa yoki har qanday umumiy mavzuda shunchaki suhbatlashmoqchi bo'lsa (masalan: "Bugun ob-havo qanday?", "Dasturlash haqida gaplashaylik", "Charchadim"), unga xuddi yaqin do'stidek samimiy, jonli va odamday javob qaytar. Bu holatlarda YANGILIK QIDIRMA va toolni mutlaqo chaqirma!

2. YANGILIKLAR VA MA'LUMOTLAR SO'ROVI:
   - Agar foydalanuvchi umumiy yangiliklarni so'rasa (masalan: "Yangi xabarlar bormi?", "Bugun nima gaplar?", "Yangiliklarni ko'rsat"), u holda `get_uzdaily_news` toolini chaqir va query parametriga "O'zbekiston" deb yubor.
   - Agar foydalanuvchi aniq bir davlat, xorij yoki dunyo voqealarini so'rasa (masalan: "Dunyoda nima gap?", "Xorij xabarlari"), toolni query="Dunyo" parametri bilan ishlat.
   - Agar aniq bir yo'nalish yoki kalit so'z bo'yicha ma'lumot so'ralsa (masalan: "Moliya yangiliklari", "Dollar kursi nima bo'ldi?", "Sportda nima gap?"), o'sha mavzuni (masalan: "moliya", "valyuta", "sport") ajratib olib, toolga query sifatida yubor.

3. JAVOB FORMATI:
   - Tool orqali olingan yangiliklarni foydalanuvchiga taqdim etayotganda ortiqcha gaplarni qisqartirib, chiroyli Markdown formatida, sarlavhalar va havolalar bilan tartibli qilib ko'rsat.""")

async def agent(state: State) -> State:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
    )
    llm_with_tools = llm.bind_tools(TOOLS)
    response = await llm_with_tools.ainvoke([SYSTEM] + state["messages"])
    return {"messages": [response]}


async def run_tools(state: State) -> State:
    tool_map = {t.name: t for t in TOOLS}
    last = state["messages"][-1]
    results = []
    
    for call in last.tool_calls:
        args = call.get("args", {})
        
        # Agarda AI argument uzatishda xato qilsa, shu yerda to'g'rilaymiz
        if "query" not in args or not args["query"]:
            args["query"] = "O'zbekiston"
            
        try:
            result = await tool_map[call["name"]].ainvoke(args)
        except Exception as e:
            result = f"Yangilik qidirishda texnik xatolik yuz berdi: {e}"
            
        results.append(ToolMessage(content=result, tool_call_id=call["id"]))
        
    return {"messages": results}


def should_continue(state: State) -> Literal["tools", "end"]:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "end"


graph = StateGraph(State)
graph.add_node("agent", agent)
graph.add_node("tools", run_tools)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
graph.add_edge("tools", "agent")
app = graph.compile()


async def ask(question: str) -> str:
    result = await app.ainvoke({"messages": [HumanMessage(content=question)]})
    return result["messages"][-1].content 