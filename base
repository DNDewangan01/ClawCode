# Install Python dependencies
pip install -r requirements.txt

# Install Rust toolchain (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# Build Rust components
cargo build --release

# Install the package in development mode
pip install -e .
