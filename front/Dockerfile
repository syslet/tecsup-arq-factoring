# ── Base ──
FROM node:22-alpine AS base
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app

# ── Development (HMR via Astro dev server) ──
FROM base AS development
EXPOSE 4321
ENV HOST=0.0.0.0
CMD ["sh", "-c", "pnpm install && exec pnpm dev --host 0.0.0.0"]

# ── Builder (production assets) ──
FROM base AS builder
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm run build

# ── Production (static serve via Nginx) ──
FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
