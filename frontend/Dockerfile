# -------- Vue3 Frontend (Vite) --------
# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/ .
RUN npm install --silent
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
