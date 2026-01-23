# Docker Configurations for Azure Databricks

This folder contains Docker configurations for creating custom Databricks cluster images with pre-installed packages and specialized environments.

## 📁 Available Configurations

### **R/**
R-based runtime environments for data science and statistical analysis.

**Use Cases:**
- R packages pre-installed
- Statistical modeling environments
- Data analysis workflows

---

### **alphine/**
Alpine Linux-based minimal images for optimized performance.

**Use Cases:**
- Lightweight containers
- Minimal overhead
- Fast startup times

---

### **min20/**
Minimal Ubuntu 20.04 configurations.

**Use Cases:**
- Clean Ubuntu 20.04 base
- Essential packages only
- Custom from-scratch builds

---

### **python env/**
Python environment configurations with common data science packages.

**Use Cases:**
- Python-specific workloads
- Data science libraries
- Machine learning environments

---

### **rbase/**
R base configurations with core R installation.

**Use Cases:**
- Basic R runtime
- Foundation for R projects
- Minimal R environment

---

### **rbase-std/**
Standard R configurations with commonly used packages.

**Use Cases:**
- R with standard libraries
- Enterprise R environments
- Pre-configured R setups

---

### **std20/**
Standard Ubuntu 20.04 images with common tools.

**Use Cases:**
- General-purpose environments
- Standard tooling
- Balanced configuration

---

## 🚀 How to Use

### **1. Choose a Configuration**
Browse the folders above and select the configuration that matches your needs.

### **2. Build the Image**
```bash
cd <folder-name>
docker build -t your-image-name:tag .
```

### **3. Push to Registry**
```bash
# Tag for your registry
docker tag your-image-name:tag your-registry.azurecr.io/your-image-name:tag

# Push to Azure Container Registry
docker push your-registry.azurecr.io/your-image-name:tag
```

### **4. Configure Databricks Cluster**
In your cluster configuration, specify the custom container:
```json
{
  "docker_image": {
    "url": "your-registry.azurecr.io/your-image-name:tag"
  }
}
```

---

## 📖 Documentation

For detailed information on using custom containers with Azure Databricks:
- [Azure Databricks Custom Containers](https://docs.microsoft.com/azure/databricks/clusters/custom-containers)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

---

## 💡 Tips

1. **Base Image Selection**: Choose the minimal base that meets your requirements
2. **Layer Optimization**: Combine RUN commands to reduce layer count
3. **Package Versions**: Pin specific versions for reproducibility
4. **Security**: Scan images for vulnerabilities before deployment
5. **Size**: Keep images as small as possible for faster startup

---

## 🔧 Common Customizations

### **Add Python Packages**
```dockerfile
RUN pip install numpy pandas scikit-learn
```

### **Add R Packages**
```dockerfile
RUN R -e "install.packages(c('dplyr', 'ggplot2'), repos='https://cran.r-project.org')"
```

### **Add System Packages**
```dockerfile
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*
```

---

## ⚠️ Important Notes

- Custom images must be compatible with Databricks runtime
- Images must include required Databricks components
- Test images thoroughly before production use
- Keep images updated with security patches

---

## 🆘 Troubleshooting

**Image too large:**
- Use multi-stage builds
- Clean up package manager caches
- Remove unnecessary files

**Build fails:**
- Check base image compatibility
- Verify package availability
- Review Dockerfile syntax

**Cluster won't start:**
- Verify image is accessible from Databricks
- Check container registry credentials
- Review Databricks logs

---

**Back to:** [Main Repository](../README.md)
