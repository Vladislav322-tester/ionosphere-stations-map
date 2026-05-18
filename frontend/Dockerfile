FROM node:18-bullseye
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --silent || npm install --silent
# Copy and build app
COPY . .
# Copy Cesium static assets to public/cesium so viewer can load workers and widgets
RUN mkdir -p public/cesium && cp -r node_modules/cesium/Build/Cesium/* public/cesium/
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
