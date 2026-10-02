# AI and automated-use model

Kiyoshima separates operational automation from reusable model improvement.

## Operational AI Use

An AI agent or coding assistant may act as a tool for an already-authorized principal. It inherits the principal's permission boundary and cannot create new rights.

Examples:

- an Individual asks a coding agent to refactor a permitted personal or freelance-tool fork: allowed;
- an authorized researcher indexes source for task-scoped retrieval: allowed;
- an Organization inside its evaluation period asks an agent to perform non-production compatibility analysis: allowed within that evaluation scope;
- an unlicensed Organization asks an agent to deploy the software in production: not allowed merely because the agent performed the work.

## Model Improvement Use

Training, fine-tuning, continued pretraining, reusable dataset construction, synthetic training-data generation, reusable weight selection/optimization, or other model improvement is reserved by default.

Kiyoshima AI 1.0 exists to grant these rights explicitly and can exchange them for money, revenue share, compute, API/model access, reciprocal rights, research collaboration, or other consideration.

## Provider terms matter

A user performing Operational AI Use should not upload Covered Software to a provider whose terms obtain model-training/model-improvement rights that the user does not possess. Authorization to use an agent is not authorization to sublicense reserved training rights to the provider.

## Text and data mining

The legal text additionally reserves non-research text/data-mining rights to the extent applicable law permits such reservation. For operators controlling an HTTP origin, `docs/TDM.md` explains optional mapping to the W3C TDM Reservation Protocol.
