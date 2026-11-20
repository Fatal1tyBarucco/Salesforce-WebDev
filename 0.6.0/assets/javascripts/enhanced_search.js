/**
 * Salesforce Release Notes - Enhanced Search Module
 *
 * Features:
 * - Fuzzy matching for typo tolerance (Levenshtein distance)
 * - Salesforce terminology synonyms mapping
 * - Keyboard shortcuts for quick access
 * - Recent searches persistence (localStorage)
 * - Enhanced result highlighting
 *
 * Integrates with MkDocs Material's built-in Lunr.js search.
 */

(function () {
  "use strict";

  const SF_SYNONYMS = {
    lwс: ["lwc", "lightning web components", "lightning"],
    apex: ["apex", "apex code", "salesforce apex"],
    flow: ["flow", "salesforce flow", "process builder"],
    "soql+": ["soql", "salesforce object query language"],
    sosl: ["sosl", "salesforce object search language"],
    "rest+api": ["rest api", "rest", "api"],
    "graphql+api": ["graphql api", "graphql"],
    metadata: ["metadata", "metadata api"],
    "tooling+api": ["tooling api", "tooling"],
    "ui+api": ["ui api", "uiapi"],
    omnistudio: ["omnistudio", "omni", "flexcards"],
    "field+service": ["field service", "fscloud", "fieldservice"],
    hyperforce: ["hyperforce", "hyper force", "salesforce hyperforce"],
    "agentforce+": ["agentforce", "agent force", "einstein agents"],
    einstein: ["einstein", "ai", "artificial intelligence", "copilot"],
    tableau: ["tableau", "bi", "business intelligence", "analytics"],
    slack: ["slack", "salesforce slack", "chatter"],
    mulesoft: ["mulesoft", "mule", "integration"],
    "experience+b": ["experience cloud", "community cloud", "communities", "portal"],
    crm: ["crm", "customer 360", "customer relationship"],
    "security": ["security", "authentication", "oauth", "saml", "mfa"],
    "sales+cloud": ["sales cloud", "salesforce sales", "crm sales"],
    "service+cloud": ["service cloud", "service cloud console", "contact center"],
    "marketing+cloud": ["marketing cloud", "email studio", "journey builder"],
    "commerce+cloud": ["commerce cloud", "b2c commerce", "b2b commerce", "storefront"],
    "data+cloud": ["data cloud", "customer data platform", "cdp", "data lake"],
    "platform+cache": ["platform cache", "cache", "session cache", "org cache"],
    "lightning+console": ["lightning console", "console app", "service console"],
    "salesforce+functions": ["functions", "compute", "serverless"],
    "change+data+capture": ["cdc", "change data capture", "streaming api"],
    "platform+events": ["platform events", "pub/sub", "event bus"],
    "custom+metadata": ["custom metadata", "metadata types", "settings"],
    "sandbox": ["sandbox", "sandbox refresh", "copy sandbox", "developer sandbox"],
    "permission+sets": ["permission sets", "permissions", "access control"],
    "profiles": ["profiles", "user profiles", "system admin"],
    "sharing+rules": ["sharing rules", "sharing", "record access"],
    "triggers": ["triggers", "apex trigger", "before insert", "after update"],
    "batch+apex": ["batch apex", "batchable", "schedule batch"],
    "future+methods": ["future methods", "future", "async apex"],
    "queueable": ["queueable", "queueable apex", "chained jobs"],
    "schedulable": ["schedulable", "scheduled apex", "cron"],
    "visualforce": ["visualforce", "vf", "pages"],
    "aura+components": ["aura", "aura components", "lightning components legacy"],
    "lwc": ["lwc", "lightning web components"],
    "sobject": ["sobject", "s object", "custom object", "standard object"],
    "dml": ["dml", "insert", "update", "delete", "upsert"],
    "Governor+limits": ["governor limits", "limits", "cpu limit", "soql limit"],
    "bulk+api": ["bulk api", "bulk", "data loader"],
    "pubsub+api": ["pubsub api", "pubsub", "realtime events"],
    "composite+api": ["composite api", "composite", "subrequests"],
    "connect+api": ["connect api", "chatter api", "feed"],
    "analytics+api": ["analytics api", "lens", "dashboards api"],
    "clouds": ["clouds", "salesforce clouds", "products"],
  };

  const FUZZY_THRESHOLD = 0.75;

  function levenshteinDistance(a, b) {
    if (a.length === 0) return b.length;
    if (b.length === 0) return a.length;
    const matrix = [];
    for (let i = 0; i <= b.length; i++) {
      matrix[i] = [i];
    }
    for (let j = 0; j <= a.length; j++) {
      matrix[0][j] = j;
    }
    for (let i = 1; i <= b.length; i++) {
      for (let j = 1; j <= a.length; j++) {
        if (b.charAt(i - 1) === a.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }
    return matrix[b.length][a.length];
  }

  function fuzzyMatch(term, text) {
    const normalized = text.toLowerCase();
    const termLower = term.toLowerCase();

    if (normalized.includes(termLower)) return 1.0;

    const distance = levenshteinDistance(termLower, normalized.substring(0, termLower.length + 3));
    const maxLen = Math.max(termLower.length, normalized.length);
    const similarity = 1 - distance / maxLen;

    return similarity >= FUZZY_THRESHOLD ? similarity : 0;
  }

  function expandWithSynonyms(term) {
    const expanded = [term];
    const termLower = term.toLowerCase();

    for (const [canonical, synonyms] of Object.entries(SF_SYNONYMS)) {
      if (
        canonical.replace(/\+/g, " ").includes(termLower) ||
        synonyms.some((s) => s.includes(termLower))
      ) {
        expanded.push(canonical.replace(/\+/g, " "));
        synonyms.forEach((s) => expanded.push(s));
      }
    }

    return [...new Set(expanded)];
  }

  function getRecentSearches() {
    try {
      return JSON.parse(localStorage.getItem("sf_release_searches") || "[]");
    } catch {
      return [];
    }
  }

  function saveSearch(term) {
    try {
      const recent = getRecentSearches();
      const filtered = recent.filter((t) => t !== term);
      filtered.unshift(term);
      localStorage.setItem("sf_release_searches", JSON.stringify(filtered.slice(0, 5)));
    } catch {
      // localStorage not available
    }
  }

  function highlightText(text, terms) {
    if (!terms || terms.length === 0) return text;
    let result = text;
    terms.forEach((term) => {
      if (term.length < 2) return;
      const regex = new RegExp(`(${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
      result = result.replace(regex, "<mark>$1</mark>");
    });
    return result;
  }

  function initSearchEnhancements() {
    const searchInput = document.querySelector(".md-search__input");
    if (!searchInput) return;

    let debounceTimer;

    searchInput.addEventListener("input", function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const term = this.value.trim();
        if (term.length >= 2) {
          const expanded = expandWithSynonyms(term);
          const fuzzyResults = [];

          document.querySelectorAll(".md-search-result__article").forEach((article) => {
            const title = article.querySelector(".md-search-result__title")?.textContent || "";
            const text = article.querySelector(".md-search-result__teaser")?.textContent || "";

            let bestScore = 0;
            expanded.forEach((t) => {
              const titleScore = fuzzyMatch(t, title) * 2;
              const textScore = fuzzyMatch(t, text);
              bestScore = Math.max(bestScore, titleScore, textScore);
            });

            if (bestScore > 0) {
              article.dataset.fuzzyScore = bestScore;
              fuzzyResults.push(article);
            }
          });

          fuzzyResults.sort((a, b) => {
            return parseFloat(b.dataset.fuzzyScore) - parseFloat(a.dataset.fuzzyScore);
          });

          fuzzyResults.forEach((article) => {
            article.style.setProperty("--fuzzy-boost", article.dataset.fuzzyScore);
          });
        }
      }, 200);
    });

    searchInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        saveSearch(this.value.trim());
      }

      if (e.key === "Escape" && document.activeElement === searchInput) {
        searchInput.blur();
      }
    });

    const recentSearches = getRecentSearches();
    if (recentSearches.length > 0 && searchInput.value === "") {
      searchInput.setAttribute("placeholder", "Search... (recent: " + recentSearches[0] + ")");
    }
  }

  document.addEventListener("DOMContentLoaded", initSearchEnhancements);
})();
