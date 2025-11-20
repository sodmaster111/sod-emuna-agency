FROM node:20-alpine
WORKDIR /app

RUN mkdir -p public

COPY package.json ./
RUN npm install

COPY . .

RUN npm run build

CMD ["npm", "start"]
