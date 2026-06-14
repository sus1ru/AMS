FROM node:20-alpine

RUN mkdir -p /app
WORKDIR /app

COPY package*.json /app
RUN npm ci
RUN rm /app/package*.json

EXPOSE 5173

CMD ["npm", "run", "build"]
