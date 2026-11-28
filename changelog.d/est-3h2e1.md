test(workflows): pin `derived_contract`'s reply-contract sentence.

Sprint101 #9 made the runner state the JSON reply contract itself whenever a
node carries a `schema`, but no test referenced the function. The new battery
pins the guards (only a non-empty dict with at least one usable required key
speaks; properties alone stay silent), the fixed opener, schema-order key
listing, and type annotation that degrades to `any` for absent, non-dict, or
type-less property entries without ever crashing on garbage schema input.
