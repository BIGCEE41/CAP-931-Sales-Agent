
import os
import re
import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup


load_dotenv()

st.set_page_config(
    page_title="CAP 931 | Sales Intelligence Agent",
    page_icon="📊",
    layout="wide",
)

def fetch_website_text(url):
    """Retrieve readable text from a public website."""
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()

        text = " ".join(soup.stripped_strings)
        return text[:6000]

    except requests.RequestException as error:
        return f"Website text could not be retrieved: {error}"




BANNED_PHRASES = [
    "time savings",
    "save selling time",
    "reduces research time",
    "reduce research time",
    "quick, up-to-date knowledge",
    "up-to-date knowledge",
    "guarantees coverage",
    "guarantee coverage",
    "eliminates unverified",
    "eliminating unverified",
    "eliminates ambiguity",
    "eliminating ambiguity",
    "ensures no unverified",
    "ensure no unverified",
    "all facts are directly supported",
    "directly supported by the retrieved website text",
    "preventing the presentation of unverified",
    "prevent the presentation of unverified",
    "all facts are verified",
    "every fact is directly supported",
    "every fact is verified",
    "all statements are verified",
    "deeper insights",
    "deeper account research",
    "data enrichment",
    "team sharing",
    "automating the research",
    "automate research",
    "research-driven insights",
]


STAT_PATTERN = re.compile(r'[\$\u20ac\u00a3]?\d[\d,\.]*\s*(?:[TMBK]\+?|\+|%)')


def audit_briefing(briefing, source_text):
    """Deterministically check a briefing for banned claims and unverified statistics."""
    findings = {"banned": [], "verified_stats": [], "unverified_stats": []}

    lowered = briefing.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            findings["banned"].append(phrase)

    source_norm = re.sub(r'\s+', '', source_text).lower()
    seen = set()
    for match in STAT_PATTERN.finditer(briefing):
        token = match.group(0)
        norm = re.sub(r'\s+', '', token).lower()
        if norm in seen:
            continue
        seen.add(norm)
        if norm in source_norm:
            findings["verified_stats"].append(token)
        else:
            findings["unverified_stats"].append(token)

    return findings

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)




st.title("Sales Intelligence Agent")
st.caption(
    "CAP 931 Capstone | AI-powered account research "
    "for sales representatives"
)

st.info(
    "Enter the details below to prepare a research briefing "
    "for your prospective customer."
)

with st.form("sales_research_form"):
    st.subheader("Product Information")

    product_name = st.text_input(
        "Product Name",
        placeholder="Example: Enterprise AI Analytics Platform",
    )

    product_category = st.text_input(
        "Product Category",
        placeholder="Example: Data Analytics",
    )

    value_proposition = st.text_area(
        "Value Proposition",
        placeholder="What business problem does your product solve?",
    )

    st.subheader("Prospective Account")

    company_url = st.text_input(
        "Target Company URL",
        placeholder="https://www.example.com",
    )

    manual_website_text = st.text_area(
        "Website Text (Optional Backup)",
        placeholder="Paste website text if automatic retrieval fails.",
    )

    competitor_urls = st.text_area(
        "Competitor URLs",
        placeholder="Enter one competitor URL per line",
    )

    target_customer = st.text_input(
        "Target Customer",
        placeholder="Name or job title of your sales contact",
    )

    submitted = st.form_submit_button(
        "Generate Sales Briefing",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not product_name.strip():
        st.error("Please enter a product name.")
    elif not company_url.strip():
        st.error("Please enter the target company URL.")
    else:
        
        with st.spinner("Generating your sales briefing..."):
            website_text = fetch_website_text(company_url)
            
            competitor_research = ""

            if competitor_urls.strip():
                for competitor_url in competitor_urls.splitlines():
                    competitor_url = competitor_url.strip()

                    if competitor_url:
                        competitor_text = fetch_website_text(competitor_url)
                        if competitor_text.startswith("Website text could not be retrieved:"):
                            st.warning(f"Could not retrieve competitor website: {competitor_url}")
                        else:
                            st.success(f"Competitor website retrieved successfully: {competitor_url}")
                        competitor_research += (
                            f"\n\nCompetitor URL: {competitor_url}\n"
                            f"Retrieved website content:\n{competitor_text}\n"
                        )

            if website_text.startswith("Website text could not be retrieved:"):
                st.warning("Website content could not be retrieved. The briefing may rely on assumptions.")
            else:
                st.success(f"Website content retrieved successfully ({len(website_text)} characters).")

            if website_text.startswith("Website text could not be retrieved:") and manual_website_text.strip():
                website_text = manual_website_text.strip()

           

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                max_tokens=4096,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            
"You are a rigorous, evidence-first sales intelligence analyst. "
"Prioritize factual accuracy, useful detail, and transparency. "

"Never present an unverified product feature, integration, "
"security control, certification, statistic, price, or customer "
"result as fact. The user's product description is not independent "
"evidence. Do not claim that a product supports CRM integration, "
"role-based access, audit trails, or enterprise security unless "
"the supplied evidence explicitly supports each claim. If evidence "
"is missing, state 'Not verified from the supplied sources.' "

"Treat user-provided product descriptions as unverified until supported "
"by evidence. Use target-company website text only as evidence about "
"that company, not as proof of the user's product capabilities. "

"Never claim a website or competitor was researched unless its content "
"was actually retrieved. A URL alone is not evidence. "

"Separate source-supported facts, reasonable inferences, and unknowns. "
"Label inferences clearly. Never invent or estimate statistics. Omit "
"unsupported numbers and unsupported product claims entirely. "

"Extract as many relevant, distinct, well-supported details as possible. "
"Prefer specific evidence over generic sales advice. Do not present "
"potential customer needs as confirmed facts. "

"Create these sections: Executive Summary, Evidence-Backed Account "
"Findings, Potential Customer Needs, Suggested Value Proposition, "
"Discovery Questions, Risks and Unknowns, and Recommended Next Steps. "

"Identify source URLs for factual findings when available. Never invent "
"citations or claim to have browsed sources that were not retrieved. "
"Explain what additional research is needed when evidence is limited. "

"Provide a useful but explicitly limited briefing. Never end "
"with a blanket claim that all statements are verified; explicitly "
"distinguish sourced facts, assumptions, recommendations, and unknowns."
"Keep the entire briefing concise (under 800 words) so it finishes completely; "
"never truncate before the final source note."

"Do not expand the user's product description into additional "
"capabilities. In particular, do not claim contact details, buying "
"signals, CRM integrations, data syncing, outreach templates, security "
"certifications, pricing, or measurable business results unless the "
"supplied evidence explicitly confirms them. In the value proposition, "
"describe only the product's stated capabilities. Label any proposed "
"future capability as a possibility to investigate, not an existing feature. "
"The final note must accurately distinguish verified facts, assumptions, "
"recommendations, and unknowns; never claim that all statements are "
"verified when the briefing contains inferences or recommendations."

"Do not add benefits, workflows, or outcomes that are not explicitly stated "
"in the product description. Do not claim the product consolidates data, "
"provides a single view, creates tailored outreach strategies, or improves "
"efficiency unless the supplied evidence explicitly supports those claims. "


"Use only details explicitly supported by the supplied website text. "
"Before including a statistic, customer count, integration count, or case-study result, "
"verify that the exact claim appears in the supplied text. "
"If the text does not support the claim, omit it. "
"Quote statistics exactly as the source states them; never split, combine, round, or rephrase figures. "
"Never attribute one company's figures to another company."
"For each statistic or key factual claim, show the exact quoted phrase from the retrieved website text as supporting evidence; "
"a source URL alone is never sufficient evidence that a number appears in the text."
"Do not infer that a claim was verified merely because a source URL is listed. "

"Base factual findings on the website text actually retrieved by the application. "
"Do not claim every fact is verified unless the retrieved text directly supports it. "
"Clearly distinguish source-supported facts, assumptions, recommendations, and unknowns. "
"Describe SalesIntel AI only using capabilities explicitly stated in the supplied product description. "
"Do not claim it provides enriched data, data-driven insights, team sharing, lead enrichment, CRM integration, or measurable benefits unless the evidence explicitly confirms them. "
"Keep suggested value propositions within the confirmed capabilities, and label any proposed future uses as possibilities to investigate. "
"In Suggested Value Proposition, write no more than two sentences restating only the product's confirmed purpose. "
"Do not describe features, workflows, speed, or benefits."
"Do not claim the tool eliminates, prevents, or guarantees the absence of unverified statements, errors, or inaccuracies. "
"Describe only what the tool does; never promise infallible results."
"Do not claim the product reduces research time, delivers quick or up-to-date knowledge, guarantees coverage, "
"or produces any other unmeasured benefit or outcome."
"Do not claim the retrieved text was the sole source of factual evidence unless every finding has been "
"checked against the actual retrieved text."
"Never use the phrase deeper insights anywhere in the briefing, including in discovery questions."
"Never describe facts as directly supported by the retrieved website text; instead state only which "
"statistics were checked against the retrieved text."




                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Product: {product_name}\n"
                            f"Category: {product_category or 'Not specified'}\n"
                            f"Value proposition: {value_proposition or 'Not specified'}\n"
                            f"Target company URL: {company_url}\n"
                            f"Website content retrieved: {website_text}\n"
                            f"Competitor URLs: {competitor_urls or 'Not specified'}\n"
                            f"Competitor website research: {competitor_research or 'No competitor content retrieved.'}\n"
                            f"Target customer: {target_customer or 'Not specified'}\n\n"
                            
"Write the briefing using these sections: Executive Summary, "
"Evidence-Backed Account Findings, Potential Customer Needs "
"(clearly label assumptions), Suggested Value Proposition, "
"Discovery Questions, Risks and Unknowns, and Recommended "
"Next Steps. Use only the supplied product information, "
"target-company website text, and successfully retrieved "
"competitor research as source material. Clearly identify "
"failed website retrievals and never treat a URL alone as "
"evidence. Cite the relevant source URL for each factual "
"finding when available. Do not claim product capabilities "
"Do not add capabilities, benefits, workflows, or outcomes beyond the exact product "
"description supplied by the user. In Suggested Value Proposition, restate only the "
"confirmed purpose: helping sales representatives research prospective accounts and "
"prepare sales briefings. Do not claim automation, time savings, deeper insights, data "
"enrichment, team sharing, or HubSpot compatibility. Treat every statement about the "
"target company's website as verified only if the retrieved website text explicitly "
"supports it. End with a note that distinguishes supported facts, assumptions, "
"recommendations, and unknowns; never say all facts are verified unless each one has "
"been checked against the retrieved text. "
"Use the exact Product name supplied in the form as the product name throughout the briefing. "
"Never substitute a different product name or invent a brand name."

                        ),
                    },
                ],
            )

       

        st.subheader("AI-Generated Sales Briefing")

        briefing = response.choices[0].message.content or ""
        finish_reason = response.choices[0].finish_reason

        st.markdown(briefing)

        st.subheader("Briefing Compliance Audit")
        audit_source = (website_text or "") + "\n" + (competitor_research or "")
        audit = audit_briefing(briefing, audit_source)

        if audit["banned"]:
            st.error(
                "Banned claim(s) detected: "
                + ", ".join(f'"{p}"' for p in audit["banned"])
            )
        else:
            st.success("No banned claims detected.")

        total_stats = len(audit["verified_stats"]) + len(audit["unverified_stats"])
        if total_stats:
            st.write(
                "Statistics verified against retrieved text: "
                f'{len(audit["verified_stats"])}/{total_stats}',
            )
            if audit["unverified_stats"]:
                st.warning(
                    "Unverified statistics (not found in retrieved text): "
                    + ", ".join(audit["unverified_stats"])
                )
        else:
            st.info("No statistics found to verify.")

        if finish_reason == "length":
            st.warning(
                "The AI response reached its output limit and may be incomplete. "
                "Please generate the briefing again."
            )
        elif not briefing.strip():
            st.error("The AI returned an empty briefing. Please try again.")



st.divider()
st.caption("CAP 931 Sales Intelligence Agent | Prototype")
