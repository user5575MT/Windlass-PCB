# WLC2 protocol for the Pi bridge

23 November 2026, Sydney time. This is the command path `firmware/s3` implements. The prototype `WLC1` / `WLC1CMD` bytes were not recovered and are not accepted. The existing Pi bridge and the prototype firmware are not modified by this repository. The bridge has to be updated to this specification before it can run the windlass.

SoftAP association is not authentication. The HMAC is the authentication.

## Shared rules

Multi-byte integers are big-endian. The tag is HMAC-SHA256 over every preceding byte, using the raw bytes of `COMMAND_KEY`. The key is at least 16 bytes. A tag that does not match is dropped: no acknowledgement, no change to the relays.

| Item | Value |
| --- | --- |
| SoftAP SSID | `WindlassCounter` |
| SoftAP password | `WIFI_PASS`, separate from the command key |
| Command | UDP port 4212, unicast to the controller |
| Telemetry | UDP port 4210, broadcast `255.255.255.255`, about every 200 ms |
| Magic | ASCII `WLC2` |
| Version | 1 |

The controller answers a valid command from the source address and source port. The answer is an ack, not a repeat of the command.

## Session, 16 bytes

The session is the 16 bytes carried in every datagram. Its lowercase hex form is what the controller compares.

| Bytes | Contents |
| --- | --- |
| 0–3 | Boot entropy A |
| 4–7 | Boot entropy B. The high nibble of byte 6 is forced to `4` |
| 8–11 | The high two bits of byte 8 are forced to `10`. The rest is the other entropy |
| 12–15 | Generation, starting at 1 |

Generation advances when a running hold is stopped, when the TTL expires, when the two directions conflict, when the coil rail drops, or when the command socket drops. A RUN on an old generation does nothing. After that advance, a STOP on the new generation clears the lock and does not energise a coil. The next RUN on that generation can start.

The ack carries the session after the command has been applied. A STOP that was holding the windlass therefore returns the new session.

## Command, 61 bytes, port 4212

| Offset | Size | Field |
| --- | --- | --- |
| 0 | 4 | `WLC2` |
| 4 | 1 | Version `1` |
| 5 | 1 | Type `1` |
| 6 | 16 | Session |
| 22 | 4 | Sequence. Greater than 0 and strictly greater than the last accepted sequence of this session |
| 26 | 1 | Op: `0` STOP, `1` UP, `2` DOWN, `3` BOTH |
| 27 | 2 | TTL in milliseconds. The controller clamps this to 150–1000. Use 300 |
| 29 | 32 | HMAC-SHA256 |

UP hauls chain in. DOWN pays chain out. BOTH, or the opposite direction while a hold is running, drops both outputs and advances the session. A repeated sequence does not refresh the hold.

Send a fresh sequence before the TTL expires. At 300 ms, a refresh about every 200 ms leaves margin. When the packets stop, the outputs and GPIO1 go low at the deadline and the session advances.

## Ack, 59 bytes

Sent only after a valid tag.

| Offset | Size | Field |
| --- | --- | --- |
| 0 | 4 | `WLC2` |
| 4 | 1 | Version `1` |
| 5 | 1 | Type `2` |
| 6 | 16 | Session after the command |
| 22 | 4 | Sequence from the command |
| 26 | 1 | `1` accepted, `0` rejected |
| 27 | 32 | HMAC-SHA256 |

A rejected command does not move an output. If the session was wrong, the ack session is the one to use next.

## Telemetry, 66 bytes, port 4210

| Offset | Size | Field |
| --- | --- | --- |
| 0 | 4 | `WLC2` |
| 4 | 1 | Version `1` |
| 5 | 1 | Type `3` |
| 6 | 16 | Current session |
| 22 | 4 | Chain pulses, signed |
| 26 | 4 | Chain millimetres, signed, saturated to 32 bits |
| 30 | 2 | Millimetres per pulse |
| 32 | 1 | Flags |
| 33 | 1 | Sensed direction: `0` stopped, `1` up, `2` down, `3` both |
| 34 | 32 | HMAC-SHA256 |

Flags: bit 0 running, bit 1 fault, bit 2 start locked, bit 3 UP request, bit 4 DOWN request, bit 5 GPIO1 high. Ignore a telemetry datagram whose tag does not match.

## What the bridge does

1. Join `WindlassCounter`.
2. Read a telemetry datagram, check the tag, and keep the session and the flag bits.
3. To run, send UP or DOWN with that session, sequence 1, TTL 300. Increment the sequence on every datagram, including refreshes.
4. To stop, send STOP. Read the session in the ack. If a hold was running, that session is new.
5. If bit 2 is set, send STOP on the current session before the next UP or DOWN. That STOP clears the lock and does not start a motor.
6. Do not send BOTH, and do not send the other direction while a hold is running. Both of those fail off.

## Test vector

Key, 32 bytes: `0123456789abcdef0123456789abcdef`

Boot entropy `0x11223344` and `0x55667788`, generation 1. Session hex `11223344556647888000000000000001`.

UP, sequence 1, TTL 300, 61 bytes:

```text
574c43320101112233445566478880000000000000010000000101012c977945be88d1a5a1b6888ac900bdf8de2aa7f71c9563e4c6f0c5e5d45eac785e
```

The host test in `firmware/s3` checks this vector, the RFC 4231 HMAC case, STOP, a bad tag, a replayed sequence, and a retired session.
