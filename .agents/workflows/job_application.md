---
description: How to automate job applications using the browser subagent.
---

# Job Application Automation Protocol

This workflow dictates how the browser subagent applies to technical roles on behalf of Bradley Ren Bates.

**CRITICAL RULE:** The subagent MUST check in and return control to the user BEFORE clicking any final "Submit Application" button. The subagent should navigate the application, fill out all fields, upload documents, reach the "Review" page, and then STOP. The subagent must present a screenshot of the final review page and wait for the user to manually submit or provide explicit permission.

## Target Roles & Exclusions
*   **Target Roles:** GenAI Architect, Platform Engineer, Data Engineer, Software Engineer, Application Engineer, specialized AI/Builder roles.
*   **EXCLUSIONS:** Do NOT apply for roles with "Senior," "Principal," or "Lead" in the title unless explicitly instructed otherwise by the user. Emphasize hands-on building capability over formal titles.

## Profile Information to Use
*   **Name:** Bradley Ren Bates
*   **Location:** Charlotte, NC
*   **Email:** `bradleybates1@gmail.com`
*   **Phone Number:** 704-555-0199 (Use only if absolutely necessary)
*   **LinkedIn URL:** https://www.linkedin.com/in/bradley-bates-792871387/
*   **Work Authorization:** Legally authorized to work in the US. No sponsorship required now or in the future.
*   **Education:** No Bachelor's degree. Emphasize military background and hands-on architecture experience.

## Work Experience (Approximate Dates Only)
Do not attempt to scrape exact dates. Use the following:
1.  **Senior Agentic Systems Architect (Self/Projects)**
    *   *Dates:* Jan 2023 - Present
    *   *Tasks/Description:* Built TURBOCOG (deterministic MTG agentic runtime), HAL (emotional memory agent with Qdrant), and T-SCAN (LLM interpretability suite). Maintained a 10x shipping velocity co-building with Cursor and Claude Code.
2.  **Tech Lead at GoDaddy**
    *   *Dates:* Jan 2009 - Jan 2012
    *   *Location:* Charlotte, NC
    *   *Tasks/Description:* Led senior engineering teams in a high-scale, multi-tenant SaaS environment. Responsible for technical leadership and system architecture.
3.  **Boiler Operator Supervisor at US Navy**
    *   *Dates:* Dec 2005 - Jun 2008
    *   *Tasks/Description:* Managed mission-critical, high-pressure steam systems as a Boiler Operator Supervisor (E-5). 

## Browsing & Form Strategy
1.  **Leverage Existing Sessions:** The browser is already authenticated into LinkedIn and the user's primary Google account. Use this to bypass authentication walls.
2.  **Autofill Advantage:** Take advantage of the Google account's native browser autofill by clicking into fields (like Name, Address, Phone) to trigger dropdowns rather than typing manually when possible.
3.  **Focus on Easy Apply:** Prioritize LinkedIn Jobs with "Easy Apply" to mitigate the action limit of the browser subagent. Only navigate to external Workday / Lever / Greenhouse portals if explicitly requested or if it's the only option for a highly targeted role. 
4.  **No Templated Language:** If cover letters or text-area responses are required, use the specific customized language from the current context and substitute explicit tags like `[Target Role Name]`. Do not use generic AI-generated templates.
