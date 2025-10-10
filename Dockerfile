# 1️⃣ Use the official Python 3.12 image
FROM python:3.12-slim

# 2️⃣ Set working directory inside container
WORKDIR /app

# 3️⃣ Copy all project files into container
COPY . .

# 4️⃣ Install uv (your package manager)
RUN pip install uv

# 5️⃣ Install all dependencies
RUN uv sync --frozen

# 6️⃣ Set PYTHONPATH so imports work
ENV PYTHONPATH=/app/src:/app/clients/python

# 7️⃣ Expose FastAPI port
EXPOSE 8000

# 8️⃣ Command to run FastAPI
CMD ["uv", "run", "uvicorn", "src.mail_client_service.src.mail_client_service.app:app", "--host", "0.0.0.0", "--port", "8000"]

