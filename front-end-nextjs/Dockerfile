FROM node:20 As base

WORKDIR /usr/src/app

COPY package.json package.json
RUN npm install

COPY . .

FROM base As developmet
EXPOSE 3000
CMD [ "npm" , "run"  , "dev"]


FROM base As production
EXPOSE 3000
RUN npm run build
CMD ["npm", "start"]



