# Future firmware heartbeat contract

This contract is the one implemented by `firmware/s3` on the integrated board. It does not change `WindlassController` on the prototype. That image does not toggle GPIO1, `ENABLE_RELAY_CONTROL` defaults off, and it must stay that way. Do not flash it, and do not edit it to satisfy this document. The prototype sources are not in this repository.

GPIO1 is `WDI_FUTURE`. The 74LVC1G123 retriggers only on a rising edge. A high level, including a pin stuck high, does not hold `WDT_Q`. R52 is 100 kΩ and C50 is 3.3 µF. The Nexperia formula for that capacitor is tW = K × REXT(kΩ) × CEXT(pF) nanoseconds, with K about 1. The typical pulse is 330 ms. The short case used for the edge spacing is K = 1 and capacitance 20% low, 264 ms. The long case is K = 1.2 and capacitance 20% high, about 475 ms. After the last edge, `Q` falls and the series MOSFET opens.

`firmware/s3` raises GPIO1 for 40 ms every 80 ms, and only while the decision core has a legal single-direction hold. Eighty milliseconds is inside the 100 ms bound below, and two edges fit inside the 264 ms short pulse. STOP, a conflicting command, loss of the command link, coil-rail loss, and expiry of the 300 ms software TTL clear GPIO1, GPIO9, and GPIO10 in the same step. A hold starts only from a WLC2 datagram whose HMAC matches `COMMAND_KEY`. The placeholder key does not open the socket, so that build never starts a hold.

## When edges are allowed

A rising edge on GPIO1 is produced only while every one of these is true:

- This image is the one built for this PCB, and relay control is enabled in that image.
- The command is authenticated under the session rules. SoftAP presence is not authentication.
- The command is a valid RUN, UP or DOWN, and it has not expired. The software TTL stays 300 ms by default, clamped from 150 ms to 1000 ms.
- No force-stop is latched.
- Communications that carried the command are still valid.
- The permissives this firmware can see are satisfied, including `COIL_RAIL_OK` on GPIO14.

The edge period is 100 ms or shorter, so a missing edge drops the coil inside one timer pulse rather than waiting out a long gap.

## When edges stop

On STOP, loss of communications, an invalid command, or TTL expiry, the firmware does both of these, independently:

1. Stop edges. Hold GPIO1 low. Do not keep toggling it from a timer.
2. Drive `UP_REQ` (GPIO9) and `DN_REQ` (GPIO10) low.

A periodic interrupt that kicks GPIO1 because `loop()` is running is forbidden. That pattern would keep a stuck-high request GPIO energised for as long as the CPU keeps looping, which is the fault the timer exists to cover.

The hardware already drops the coil if edges stop, even if one request pin is stuck high. It does not drop the coil if firmware keeps producing edges during that fault. The XOR still blocks both request pins being high together. The physical relay-power switch and the ignition contact remove coil power without any GPIO.

The 300 ms software TTL and this heartbeat are different mechanisms. The TTL clears a GPIO the CPU can still write. The heartbeat releases a GPIO the CPU can no longer change, and only after edges have stopped.
