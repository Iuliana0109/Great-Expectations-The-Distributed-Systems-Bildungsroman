# Use Node.js official image
FROM node:14

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the gateway port
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]
