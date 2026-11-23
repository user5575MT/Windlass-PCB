#include "windlass/sha256.hpp"

#include <cstring>

namespace windlass {
namespace {

uint32_t rotr(uint32_t value, uint32_t bits) { return (value >> bits) | (value << (32 - bits)); }

uint32_t load_be(const uint8_t* p) {
  return (static_cast<uint32_t>(p[0]) << 24) | (static_cast<uint32_t>(p[1]) << 16) |
         (static_cast<uint32_t>(p[2]) << 8) | static_cast<uint32_t>(p[3]);
}

void store_be(uint8_t* p, uint32_t value) {
  p[0] = static_cast<uint8_t>(value >> 24);
  p[1] = static_cast<uint8_t>(value >> 16);
  p[2] = static_cast<uint8_t>(value >> 8);
  p[3] = static_cast<uint8_t>(value);
}

const uint32_t kRound[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2};

}  // namespace

Sha256::Sha256() {
  state_[0] = 0x6a09e667;
  state_[1] = 0xbb67ae85;
  state_[2] = 0x3c6ef372;
  state_[3] = 0xa54ff53a;
  state_[4] = 0x510e527f;
  state_[5] = 0x9b05688c;
  state_[6] = 0x1f83d9ab;
  state_[7] = 0x5be0cd19;
}

void Sha256::transform(const uint8_t block[64]) {
  uint32_t w[64];
  for (int i = 0; i < 16; ++i) w[i] = load_be(block + 4 * i);
  for (int i = 16; i < 64; ++i) {
    const uint32_t s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3);
    const uint32_t s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10);
    w[i] = w[i - 16] + s0 + w[i - 7] + s1;
  }
  uint32_t a = state_[0], b = state_[1], c = state_[2], d = state_[3];
  uint32_t e = state_[4], f = state_[5], g = state_[6], h = state_[7];
  for (int i = 0; i < 64; ++i) {
    const uint32_t S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
    const uint32_t ch = (e & f) ^ ((~e) & g);
    const uint32_t temp1 = h + S1 + ch + kRound[i] + w[i];
    const uint32_t S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
    const uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
    const uint32_t temp2 = S0 + maj;
    h = g;
    g = f;
    f = e;
    e = d + temp1;
    d = c;
    c = b;
    b = a;
    a = temp1 + temp2;
  }
  state_[0] += a;
  state_[1] += b;
  state_[2] += c;
  state_[3] += d;
  state_[4] += e;
  state_[5] += f;
  state_[6] += g;
  state_[7] += h;
}

void Sha256::update(const uint8_t* data, std::size_t length) {
  for (std::size_t i = 0; i < length; ++i) {
    block_[used_++] = data[i];
    if (used_ == 64) {
      transform(block_);
      bits_ += 512;
      used_ = 0;
    }
  }
}

void Sha256::final(uint8_t out[32]) {
  uint64_t total_bits = bits_ + static_cast<uint64_t>(used_) * 8;
  block_[used_++] = 0x80;
  if (used_ > 56) {
    while (used_ < 64) block_[used_++] = 0;
    transform(block_);
    used_ = 0;
  }
  while (used_ < 56) block_[used_++] = 0;
  for (int i = 7; i >= 0; --i) block_[used_++] = static_cast<uint8_t>(total_bits >> (8 * i));
  transform(block_);
  for (int i = 0; i < 8; ++i) store_be(out + 4 * i, state_[i]);
}

void sha256(const uint8_t* data, std::size_t length, uint8_t out[32]) {
  Sha256 hash;
  hash.update(data, length);
  hash.final(out);
}

void hmac_sha256(const uint8_t* key, std::size_t key_length, const uint8_t* data, std::size_t data_length,
                 uint8_t out[32]) {
  uint8_t keyed[64] = {};
  if (key_length > 64) {
    sha256(key, key_length, keyed);
  } else if (key != nullptr && key_length > 0) {
    std::memcpy(keyed, key, key_length);
  }
  uint8_t ipad[64];
  uint8_t opad[64];
  for (int i = 0; i < 64; ++i) {
    ipad[i] = static_cast<uint8_t>(keyed[i] ^ 0x36);
    opad[i] = static_cast<uint8_t>(keyed[i] ^ 0x5c);
  }
  Sha256 inner;
  inner.update(ipad, 64);
  if (data != nullptr && data_length > 0) inner.update(data, data_length);
  uint8_t inner_hash[32];
  inner.final(inner_hash);
  Sha256 outer;
  outer.update(opad, 64);
  outer.update(inner_hash, 32);
  outer.final(out);
}

bool mac_equal(const uint8_t* left, const uint8_t* right, std::size_t length) {
  uint8_t diff = 0;
  for (std::size_t i = 0; i < length; ++i) diff |= static_cast<uint8_t>(left[i] ^ right[i]);
  return diff == 0;
}

}  // namespace windlass
