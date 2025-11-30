# Étape build Angular
FROM node:22-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
# Adapte le nom du projet Angular si besoin (ex: wakfu-frontend)
RUN npm run build -- --configuration=production

# Étape Nginx
FROM nginx:alpine
COPY --from=build /app/dist/wakstuff-frontend/browser /usr/share/nginx/html
EXPOSE 80
