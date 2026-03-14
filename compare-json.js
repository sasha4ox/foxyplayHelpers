const fs = require("fs");

function findMissingParents(obj1, obj2) {
  const missingParents = new Set();

  for (const key of Object.keys(obj1)) {
    if (!(key in obj2)) {
      missingParents.add(key);
      continue;
    }

    const val1 = obj1[key];
    const val2 = obj2[key];

    if (typeof val1 === "object" && val1 !== null) {
      const nestedKeys1 = Object.keys(val1);
      const nestedKeys2 = typeof val2 === "object" && val2 !== null ? Object.keys(val2) : [];

      for (const nestedKey of nestedKeys1) {
        if (!nestedKeys2.includes(nestedKey)) {
          missingParents.add(key);
          break;
        }
      }
    }
  }

  return Array.from(missingParents);
}

function compare(file1, file2) {
  const json1 = JSON.parse(fs.readFileSync(file1, "utf8"));
  const json2 = JSON.parse(fs.readFileSync(file2, "utf8"));

  const result = findMissingParents(json1, json2);

  console.log("Missing parent keys:");
  console.log(result);
}

const [, , file1, file2] = process.argv;

if (!file1 || !file2) {
  console.log("Usage: node compare-json.js file1.json file2.json");
  process.exit(1);
}

compare(file1, file2);