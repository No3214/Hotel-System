# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/yarn.lock* ./
RUN yarn install --frozen-lockfile || yarn install

ARG REACT_APP_BACKEND_URL=""
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

COPY frontend/ .
RUN yarn build

# Stage 2: Backend + serve frontend
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy frontend build into static_frontend
COPY --from=frontend-build /app/frontend/build ./static_frontend

EXPOSE ${PORT:-8000}

CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}
