import { migrate, pool } from "../src/lib/db";

migrate()
  .then((applied) => { console.log(applied.length ? `applied: ${applied.join(", ")}` : "schema up to date"); })
  .catch((e) => { console.error(e); process.exitCode = 1; })
  .finally(() => pool().end());
