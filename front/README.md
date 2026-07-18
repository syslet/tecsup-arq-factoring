# Frontend Client Application

This is the client-side application built with **Astro**, **TailwindCSS**, and **React** structured under **Clean Architecture**.

---

## 1. Directory Structure

The frontend isolates business logic from rendering frameworks (Astro/React) using a layered Clean Architecture:

```
front/
├── public/                 # Static assets
├── src/
│   ├── domain/             # Pure models and business entities
│   │   └── models/         # Domain model contracts and logic
│   ├── application/        # UI-agnostic application use cases
│   │   └── use-cases/      # Flow workflows and orchestration
│   ├── adapters/           # Communication and data adaptation
│   │   ├── api/            # API clients consuming backend endpoints
│   │   ├── dto/            # Data Transfer Objects (matching API structure)
│   │   └── mappers/        # Translation layer mapping DTOs <-> Domain models
│   ├── components/         # Reusable UI component modules
│   │   ├── astro/          # High-performance static Astro components
│   │   └── react/          # Highly interactive React islands (minimum hydration)
│   ├── layouts/            # Shared Astro page layout wrappers
│   ├── pages/              # Astro file-based router views (static/SSR)
│   └── styles/             # Global stylesheets and utility variables
└── tsconfig.json           # TypeScript configuration
```

---

## 2. Local Development Setup

Ensure you have [Node.js](https://nodejs.org/) installed (v20+ recommended).

### Install Dependencies
```bash
npm install
```

### Start Development Server
Launches the site at `http://localhost:4321` with HMR:
```bash
npm run dev
```

### Build for Production
Compiles Astro static files into `dist/`:
```bash
npm run build
```

---

## 3. Linting & Formatting

### Run Code Formatter (Prettier)
Formats all files and automatically sorts TailwindCSS classes:
```bash
npx prettier --write "src/**/*.{js,jsx,ts,tsx,astro,css}" --ignore-unknown
```

### Run Code Linter (ESLint)
Analyzes code for quality, TypeScript semantics, and React hook rules:
```bash
npx eslint
```
