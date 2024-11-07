# Use an official Node.js image as the base
FROM node:14

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the package.json and package-lock.json if available
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code to the container
COPY . .

# Expose the service discovery port
EXPOSE 9000

# Start the service discovery server
CMD ["node", "service_discovery.js"]
