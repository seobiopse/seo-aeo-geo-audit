# Stateful AI Memory Systems & Site Architecture

This guide details the shift from stateless Retrieval-Augmented Generation (RAG) to **Stateful AI Memory Systems**, how sites can structure their data to optimize for memory-augmented search agents, and a conceptual framework for custom stateful retrieval inside our plugin.

---

## 1. Stateless RAG vs. Stateful Memory Systems

Traditional RAG is **stateless**: it treats each search query as a separate vector lookup, retrieving local document blocks without understanding the global structure, hierarchy, or brand context of the site.

**Stateful AI Memory Systems** (conceptually inspired by architectures like MemoRAG) use a dual-system model:

```
                  ┌────────────────────────────────────────┐
                  │          Global Memory Layer           │
                  │   - Entity Graphs & Site Hierarchies   │
                  │   - /llms.txt & /llm-memory-context.json│
                  └──────────────────┬─────────────────────┘
                                     │
                     Maps Query to Target Resources
                                     │
                                     ▼
                  ┌────────────────────────────────────────┐
                  │        Local Retrieval Layer           │
                  │   - Page-Specific Vector Chunks        │
                  │   - Exact Raw HTML & Table Extractors  │
                  └────────────────────────────────────────┘
```

* **Global Memory Layer:** Understands global concepts, page hierarchies, core brand entity properties, and topical directories. It answers queries like *"What is this brand's main pricing tier and how does it relate to their product catalog?"*
* **Local Retrieval Layer:** Fetches raw, exact text chunks from specific nodes identified by the memory layer (e.g. extracting the refund policy table on `/terms`).

---

## 2. Optimizing Site Architecture for AI Memory Systems

To audit a site for stateful memory synthesis, verify the existence of these three memory structures:

### 📄 A. Root-Level Memory Files
The site must expose clear text files designed to initialize an agent's memory layer:
* **`/llms.txt` (or `/llm.txt`):** Structured markdown containing a global summary of the site, core product entities, and links to specialized text pages.
* **`/llm-memory-context.json` (Recommended Custom Entity Map):**
  A machine-readable JSON mapping the brand's core entity database to schema definitions.
  ```json
  {
    "@context": "https://schema.org",
    "brandEntity": {
      "name": "BuildingWorld",
      "wikidataId": "Q12345678",
      "coreVertical": "B2B Building Materials",
      "established": 2020
    },
    "sitemapDirectory": {
      "/products": "Main catalog listing 50,000+ construction materials",
      "/about": "Company founders, mission, and registered office details",
      "/docs": "Technical datasheets for concrete, bricks, and steel"
    }
  }
  ```

### 🕸️ B. Connected Entity `@graph` Schemas
* **Rule:** Do not write isolated JSON-LD blocks on different pages. Instead, link all pages to a central root organization entity via `@id` properties.
* **Why:** AI Memory Engines build relationships by parsing schema graphs. A product page schema should link the manufacturer entity to the company's main official social handles and headquarters.

---

## 3. Custom Plugin Methodology: The Stateful Audit Memory Cache

To enable stateful auditing within the Advanced SEO Plugin without copying exact external code bases, the agent uses a **Stateful Audit Memory Cache (SAM-C)** framework:

```
[Target Site Crawl] ──> [Extract /llms.txt & Schemas] ──> [Build Local JSON Graph]
                                                                  │
[Audit Checklist Execution] <── [Query Local Graph Cache] <───────┘
```

### ⚙️ SAM-C Execution Flow
1. **Memory Bootstrapping:**
   * When initiating `/full-audit` or `/vds-audit`, the plugin first scrapes the site's `/llms.txt`, root `/sitemap.xml`, and the homepage metadata.
   * It creates a temporary in-memory JSON file: `scratch/audit-site-memory.json`.
2. **Context Retention:**
   * Instead of reloading and re-parsing full page HTML files for every separate checklist verification step (e.g., checking titles, checking schemas, checking links), the checker queries the local memory graph first.
   * If a checklist item requires verifying author profiles, the memory layer directs the crawler straight to the `/about` node recorded in the cache, rather than scanning the whole site.
3. **Synthesis Acceleration:**
   * When compiling the final Markdown/HTML reports, the plugin uses the memory cache to match findings across templates, resolving redundancies and ensuring that layout warnings are not repeated.
