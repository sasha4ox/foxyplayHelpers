const fs = require("fs");
const { translate } = require("@vitalets/google-translate-api");

const BATCH_SIZE = 50;

function flatten(obj, prefix = "", res = {}) {
  for (const key in obj) {
    const newKey = prefix ? `${prefix}.${key}` : key;

    if (typeof obj[key] === "string") {
      res[newKey] = obj[key];
    } else if (typeof obj[key] === "object" && obj[key] !== null) {
      flatten(obj[key], newKey, res);
    }
  }

  return res;
}

function unflatten(flat) {
  const result = {};

  for (const path in flat) {
    const keys = path.split(".");
    let current = result;

    keys.forEach((k, i) => {
      if (i === keys.length - 1) {
        current[k] = flat[path];
      } else {
        current[k] = current[k] || {};
        current = current[k];
      }
    });
  }

  return result;
}

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

async function run() {
  const en = JSON.parse(fs.readFileSync("en.json", "utf8"));

  const flat = flatten(en);
  const keys = Object.keys(flat);

  const translated = {};

  console.log(`Translating ${keys.length} strings...\n`);

  let processed = 0;

  for (let i = 0; i < keys.length; i += BATCH_SIZE) {
    const batchKeys = keys.slice(i, i + BATCH_SIZE);
    const batchTexts = batchKeys.map((k) => flat[k]);

    const res = await translate(batchTexts, { to: "es" });

    res.forEach((r, index) => {
      translated[batchKeys[index]] = r.text;
    });

    processed += batchKeys.length;

    const percent = ((processed / keys.length) * 100).toFixed(1);

    process.stdout.write(
      `\rProgress: ${percent}% (${processed}/${keys.length})`
    );

    await delay(800);
  }

  const finalJson = unflatten(translated);

  fs.writeFileSync("es.json", JSON.stringify(finalJson, null, 2));

  console.log("\n\nTranslation completed ✔");
}

run();