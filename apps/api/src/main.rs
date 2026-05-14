use anyhow::Context;
use my_sifu_api::app;
use std::net::SocketAddr;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let host = std::env::var("MY_SIFU_API_HOST").unwrap_or_else(|_| "127.0.0.1".to_string());
    let port = std::env::var("MY_SIFU_API_PORT")
        .ok()
        .and_then(|value| value.parse::<u16>().ok())
        .unwrap_or(4010);
    let address: SocketAddr = format!("{host}:{port}")
        .parse()
        .with_context(|| format!("invalid API listen address: {host}:{port}"))?;

    let listener = tokio::net::TcpListener::bind(address)
        .await
        .with_context(|| format!("failed to bind API listener on {address}"))?;

    axum::serve(listener, app())
        .await
        .context("API server stopped unexpectedly")?;

    Ok(())
}
