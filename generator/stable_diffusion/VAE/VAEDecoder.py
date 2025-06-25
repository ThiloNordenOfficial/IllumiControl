from torch import nn


class VAEDecoder(nn.Module):
    def __init__(self, latent_dim, out_channels):
        super(VAEDecoder, self).__init__()
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(latent_dim, 128, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, out_channels, kernel_size=4, stride=2, padding=1),
        )

    def forward(self, x):
        return self.decoder(x)
