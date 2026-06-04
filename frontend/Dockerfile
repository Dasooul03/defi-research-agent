# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./

RUN npm config set registry https://registry.npmmirror.com && \
    npm install && npm cache clean --force

COPY . .

RUN mkdir -p /app/public

ENV NEXT_PUBLIC_API_BASE=http://localhost:8000

RUN npm run build

# Stage 2: Production runtime
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000

CMD ["node", "server.js"]
