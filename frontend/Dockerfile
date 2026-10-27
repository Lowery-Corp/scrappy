FROM node:20-alpine AS dependencies

WORKDIR /app

COPY package*.json ./
RUN npm ci

FROM dependencies AS development

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM development AS build

ARG VITE_SCRAPPYS_SCRAPYARD_URL=http://localhost:8010
ENV VITE_SCRAPPYS_SCRAPYARD_URL=${VITE_SCRAPPYS_SCRAPYARD_URL}
RUN npm run build

FROM node:20-alpine AS production

WORKDIR /app

COPY --from=build /app/package*.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist

EXPOSE 8000

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "8000"]
