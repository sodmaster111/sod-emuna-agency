# Multi-stage Next.js build optimized for offline/strict environments
FROM node:20-alpine AS deps
WORKDIR /app

# Install dependencies without requiring a pre-existing lockfile
COPY package*.json ./
RUN npm install

FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/package.json ./package.json
# Guarantee the public directory exists before copying
RUN mkdir -p public
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["npm", "start"]
