
import os
import urllib.error
import urllib.request
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


client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)




st.title("Sales Intelligence Agent")
st.success("DEBUG CHECK: This is the updated app file.")
st.success("DEBUG CHECK: This is the updated app file.")
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
            competitor_evidence = []

            if competitor_urls.strip():
                for competitor_url in competitor_urls.splitlines():
                    competitor_url = competitor_url.strip()

                    if competitor_url:
                        competitor_text = fetch_website_text(competitor_url)

                        if competitor_text.startswith("Website text could not be retrieved:"):
                            st.warning(f"Could not retrieve competitor website: {competitor_url}")
                        else:
                            st.success(f"Competitor website retrieved successfully: {competitor_url}")

                            competitor_evidence.append(
                                {
                                    "url": competitor_url,
                                    "text": competitor_text,
                                }
                            )

                            competitor_research += (
                                f"\n\nCompetitor URL: {competitor_url}\n"
                                f"Retrieved website content:\n{competitor_text}\n"
                            )

            if website_text.startswith("Website text could not be retrieved:"):
                st.warning(
                    "Website content could not be retrieved. "
                    "The briefing may rely on assumptions."
                )
            else:
                st.success(
                    f"Website content retrieved successfully "
                    f"({len(website_text)} characters)."
                )

            if (
                website_text.startswith("Website text could not be retrieved:")
                and manual_website_text.strip()
            ):
                website_text = manual_website_text.strip()

            # Display research evidence directly on the page.
            st.write("TEST: Research evidence section reached.")
            st.subheader("Research Evidence — Website Text Used")

            st.markdown("**Target company source**")
            st.write(company_url)

            st.text_area(
                "Target company website text",
                value=website_text,
                height=200,
                disabled=True,
                key="target_company_evidence",
            )

            st.markdown("**Competitor sources**")

            if competitor_evidence:
                for item in competitor_evidence:
                    st.write(item["url"])
                    st.text_area(
                        f"Retrieved text — {item['url']}",
                        value=item["text"],
                        height=200,
                        disabled=True,
                        key=f"evidence_{item['url']}",
                    )
            else:
                st.info("No competitor website text was retrieved.")

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
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
"Provide a useful but explicitly limited briefing rather than filling "
"gaps with fabricated details."

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
                            "Write a sales briefing with: Product Summary, "
                            "Likely Customer Needs (clearly label assumptions), "
                            "Suggested Value Proposition, Discovery Questions, "
                            "and Recommended Next Steps. State that only the supplied "
"target-company website text and competitor research content "
"were supplied separately. Use competitor content only when "
"retrieval succeeded. Clearly identify failed retrievals and "
"never treat a URL alone as evidence. Cite the relevant source "
"URL for each factual finding when available."
                        ),
                    },
                ],
            )

        st.subheader("AI-Generated Sales Briefing")
        st.markdown(response.choices[0].message.content)


st.divider()
st.caption("CAP 931 Sales Intelligence Agent | Prototype")
