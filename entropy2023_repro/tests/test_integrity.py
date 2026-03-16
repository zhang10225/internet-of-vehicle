from dataclasses import replace

from src.ta import keygen, setup
from src.scheme import encrypt
from src.rsu import rsu_transform
from src.obu import final_decrypt
from src.types import IntegrityError, RevocationState


def test_tampered_transformed_ciphertext_fails_integrity_check():
    pp, msk = setup()
    bundle = keygen(pp, msk, uid='veh-009', static_attrs=['role:ambulance', 'dept:traffic'])
    ciphertext = encrypt(
        pp,
        message=b'hello-iov',
        static_policy=['role:ambulance', 'dept:traffic'],
        dynamic_policy=['region:r1', 'timeslot:t1'],
    )
    transformed = rsu_transform(
        pp,
        bundle.certificate,
        bundle.transform_key,
        ciphertext,
        RevocationState(),
        context={'region:r1', 'timeslot:t1'},
    )
    tampered = replace(
        transformed,
        transformed_session_blob=bytes([transformed.transformed_session_blob[0] ^ 0x01])
        + transformed.transformed_session_blob[1:],
    )
    try:
        final_decrypt(pp, bundle.final_key, tampered)
    except IntegrityError:
        return
    raise AssertionError('expected integrity verification to fail')
