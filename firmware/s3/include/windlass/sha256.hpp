#ifndef WINDLASS_SHA256_HPP
#define WINDLASS_SHA256_HPP

#include <cstddef>
#include <cstdint>

namespace windlass {

class Sha256 {
 public:
  Sha256();
  void update(const uint8_t* data, std::size_t length);
  void final(uint8_t out[32]);

 private:
  void transform(const uint8_t block[64]);

  uint32_t state_[8];
  uint64_t bits_ = 0;
  uint8_t block_[64] = {};
  std::size_t used_ = 0;
};

void sha256(const uint8_t* data, std::size_t length, uint8_t out[32]);
void hmac_sha256(const uint8_t* key, std::size_t key_length, const uint8_t* data, std::size_t data_length,
                 uint8_t out[32]);
bool mac_equal(const uint8_t* left, const uint8_t* right, std::size_t length);

}  // namespace windlass
#endif  // WINDLASS_SHA256_HPP
