(async () => {
  const API_URL = "https://www.xing.com/xing-one/api";
  const MAX_COUNT = 2999;
  const headers = {
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0"
  };

  const specialCharMap = {
    ä: "ae",
    ö: "oe",
    ü: "ue",
    ß: "ss",
    Ä: "ae",
    Ö: "oe",
    Ü: "ue"
  };

  const normalizeName = (value) =>
    String(value || "")
      .trim()
      .replace(/\./g, "")
      .replace(/[äöüÄÖÜß]/g, (char) => specialCharMap[char] || char)
      .toLowerCase();

  const getSlugFromInput = (input) => {
    const raw = String(input || "").trim();
    if (!raw) {
      return "";
    }

    const currentMatch = window.location.href.match(/xing\.com\/pages\/([^/?#]+)/i);
    if (!raw && currentMatch) {
      return currentMatch[1];
    }

    if (/^https?:\/\//i.test(raw)) {
      const match = raw.match(/xing\.com\/pages\/([^/?#]+)/i);
      return match ? match[1] : "";
    }

    return raw.replace(/^\/+|\/+$/g, "");
  };

  const buildEmail = (firstName, lastName, syntax, domain) => {
    if (!syntax || !domain) {
      return "";
    }

    const first = normalizeName(firstName);
    const last = normalizeName(lastName);
    const replacements = {
      "{first}": first,
      "{last}": last,
      "{f}": first.slice(0, 1),
      "{l}": last.slice(0, 1)
    };

    let pattern = syntax.trim();
    const shorthand = {
      "first.last": "{first}.{last}",
      "f.last": "{f}.{last}",
      "first": "{first}",
      "last": "{last}",
      "fl": "{f}{l}",
      "flast": "{f}{last}",
      "firstl": "{first}{l}",
      "first_last": "{first}_{last}",
      "first-last": "{first}-{last}"
    };

    pattern = shorthand[pattern] || pattern;

    Object.entries(replacements).forEach(([token, value]) => {
      pattern = pattern.split(token).join(value);
    });

    return `${pattern}@${domain.trim().replace(/^@+/, "")}`;
  };

  const csvEscape = (value) => {
    const text = String(value ?? "");
    if (/[;"\n\r]/.test(text)) {
      return `"${text.replace(/"/g, '""')}"`;
    }
    return text;
  };

  const downloadCsv = (rows, filename) => {
    const csvContent = rows.map((row) => row.map(csvEscape).join(";")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  };

  const postGraphql = async (payload) => {
    const response = await fetch(API_URL, {
      method: "POST",
      headers,
      credentials: "include",
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status} while calling XING API`);
    }

    const data = await response.json();
    if (data.errors?.length) {
      throw new Error(data.errors.map((item) => item.message).join(" | "));
    }

    return data;
  };

  try {
    const currentSlugMatch = window.location.href.match(/xing\.com\/pages\/([^/?#]+)/i);
    const companyInput = currentSlugMatch
      ? currentSlugMatch[1]
      : prompt("XING company URL or slug", "https://www.xing.com/pages/appleretaildeutschlandgmbh");
    const companySlug = getSlugFromInput(companyInput);

    if (!companySlug) {
      throw new Error("No valid XING company slug provided.");
    }

    const emailSyntax = (prompt(
      "Email syntax\nExamples: first.last, f.last, first, last, fl, {first}.{last}\nLeave blank to skip email generation.",
      "first.last"
    ) || "").trim();
    const emailDomain = (prompt(
      "Email domain\nExample: company.com\nLeave blank to skip email generation.",
      "example.com"
    ) || "").trim();

    const companyPayload = {
      operationName: "EntitySubpage",
      variables: {
        id: companySlug,
        moduleType: "employees"
      },
      query:
        "query EntitySubpage($id: SlugOrID!, ) { entityPageEX(id: $id) { ... on EntityPage { slug title context { companyId } } } }"
    };

    const companyData = await postGraphql(companyPayload);
    const companyPage = companyData?.data?.entityPageEX;
    const companyId = companyPage?.context?.companyId;
    const companyTitle = companyPage?.title || companySlug;

    if (!companyId) {
      throw new Error("Could not resolve the company ID. Make sure you are logged into XING and the company page exists.");
    }

    const employeesPayload = {
      operationName: "Employees",
      variables: {
        consumer: "",
        id: companyId,
        first: MAX_COUNT,
        query: {
          consumer: "web.entity_pages.employees_subpage",
          sort: "CONNECTION_DEGREE"
        }
      },
      query:
        'query Employees($id: SlugOrID!, $first: Int, $after: String, $query: CompanyEmployeesQueryInput!, $consumer: String! = "", $includeTotalQuery: Boolean = false) { company(id: $id) { id totalEmployees: employees(first: 0, query: {consumer: $consumer}) @include(if: $includeTotalQuery) { total } employees(first: $first, after: $after, query: $query) { total edges { node { profileDetails { id firstName lastName displayName gender pageName location { displayLocation } occupations { subline } } } } } } }'
    };

    const employeesData = await postGraphql(employeesPayload);
    const edges = employeesData?.data?.company?.employees?.edges || [];

    const employees = edges
      .map(({ node }) => {
        const details = node?.profileDetails || {};
        const firstName = String(details.firstName || "").trim();
        const lastName = String(details.lastName || "").trim();

        if (!firstName && !lastName) {
          return null;
        }

        const email = emailSyntax && emailDomain ? buildEmail(firstName, lastName, emailSyntax, emailDomain) : "";

        return {
          Firstname: firstName,
          Lastname: lastName,
          ...(email ? { Email: email } : {}),
          Position: details.occupations?.[0]?.subline || "",
          Gender: details.gender || "",
          Location: (details.location?.displayLocation || "").replace(/\*\*/g, "").replace(/, /g, ","),
          Profile: details.pageName ? `https://www.xing.com/profile/${details.pageName}` : ""
        };
      })
      .filter(Boolean);

    console.info("Company Name:", companyTitle);
    console.info("Company X-ID:", companyId);
    console.info("Company Slug:", companySlug);
    if (emailSyntax && emailDomain) {
      console.info("Email Format:", `${emailSyntax}@${emailDomain.replace(/^@+/, "")}`);
    }
    console.info("Employees:", employees.length);

    console.table(employees);

    const csvRows = [
      Object.keys(employees[0] || { Firstname: "", Lastname: "", Position: "", Gender: "", Location: "", Profile: "" }),
      ...employees.map((employee) => Object.values(employee))
    ];

    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    downloadCsv(csvRows, `xing-${companySlug}-${timestamp}.csv`);
  } catch (error) {
    console.error("XingDumper failed:", error);
  }
})();
