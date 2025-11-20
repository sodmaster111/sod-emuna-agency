// SoulboundAmulet.tact
// Placeholder Tact contract for a non-transferable NFT (soulbound amulet).
// Replace with full logic once on-chain behavior is finalized.

contract SoulboundAmulet {
    owner: address;

    constructor(owner: address) {
        self.owner = owner;
    }

    receive() {
        // No-op placeholder.
    }
}
