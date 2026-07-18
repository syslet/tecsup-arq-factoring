# Stage 1: Base image
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./

# Stage 2: Development (para debugging y HMR)
FROM base AS development
RUN npm install
COPY . .
EXPOSE 4321
ENV HOST=0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Stage 3: Build para producción
FROM base AS builder
RUN npm ci
COPY . .
RUN npm run build

# Stage 4: Production Runtime (Servidor Nginx ultra-ligero)
FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
