# Future firmware heartbeat contract

This contract is for a future image built for this PCB. It does not change `WindlassController` on the prototype. That image does not toggle GPIO1, `ENABLE_RELAY_CONTROL` defaults off, and it must stay that way. Do not flash it, and do not edit it to satisfy this document.

GPIO1 is `WDI_FUTURE`. The 74LVC1G123 retriggers only on a rising edge. A high level, including a pin stuck high, does not hold `WDT_Q`. The pulse is 330 ms typical and about 475 ms in the long case. After the last edge, `Q` falls and the series MOSFET opens.

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
