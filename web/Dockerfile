# Etapa 1: Build de la aplicación Vite con Node
FROM node:20-alpine AS build

WORKDIR /app

# Instalar pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Argumentos de compilación para Vite
ARG VITE_API_BASE_URL=http://localhost:8090
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Copiar manifiestos e instalar dependencias
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile || pnpm install

# Copiar código fuente y compilar
COPY . .
RUN pnpm build

# Etapa 2: Servidor Web Nginx ligero
FROM nginx:alpine AS runner

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
