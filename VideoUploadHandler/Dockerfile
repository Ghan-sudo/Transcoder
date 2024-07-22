# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.12 as build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
WORKDIR ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}


# Install the function's dependencies
RUN pip install --target ${FUNCTION_DIR} -r req.txt

# Use Ubuntu image to reduce the final image size
FROM ubuntu:24.04

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

RUN apt-get update
RUN apt-get install -y python3

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/bin/python3", "-m", "awslambdaric" ]
# Pass the name of the function handler as an argument to the runtime
CMD [ "SetupService.Setup" ]